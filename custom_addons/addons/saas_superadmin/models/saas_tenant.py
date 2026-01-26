from odoo import models, fields, api, _
import logging
from odoo.service.db import list_dbs, exp_rename, exp_drop
from odoo.exceptions import UserError, ValidationError, AccessError
from odoo import SUPERUSER_ID
import json

class SaasTenant(models.Model):
    _name = "saas.tenant"
    _description = "SaaS Tenant"
    def _valid_field_parameter(self, field, name):
        if name == "tracking":
            return True
        return super(SaasTenant, self)._valid_field_parameter(field, name)

    name = fields.Char(string=_("Tenant Name"), required=True, tracking=True, copy=False)
    database_name = fields.Char(
        string=_("Database Name"), required=True, tracking=True, copy=False
    )
    active = fields.Boolean(string=_("Active"), default=True, tracking=True)
    state = fields.Selection(
        [
            ("draft", _("Draft")),
            ("active", _("Active")),
            ("suspended", _("Suspended")),
            ("archived", _("Archived")),
        ],
        string=_("State"),
        default="draft",
        required=True,
        tracking=True,
    )

    pack_id = fields.Many2one(
        "saas.pack", string=_("Business Pack"), tracking=True, ondelete="restrict"
    )
    company_name = fields.Char(string=_("Company Name"), required=True, tracking=True)
    admin_email = fields.Char(string=_("Admin Email"), required=True, tracking=True)
    admin_password = fields.Char(string=_("Admin Password"), help=_("Password for admin user (used only during creation)"))
    admin_phone = fields.Char(string=_("Admin Phone"))

    user_count = fields.Integer(
        string=_("Nombre d'utilisateurs"), compute="_compute_user_count", readonly=True
    )
    max_users = fields.Integer(string=_("Max Users"), default=100, required=True)
    user_limit_reached = fields.Boolean(
        string=_("User Limit Reached"), compute="_compute_user_limit_reached", store=True
    )


    notes = fields.Text(string=_("Notes"))
    creation_date = fields.Datetime(
        string=_("Creation Date"), default=fields.Datetime.now, readonly=True
    )
    activation_date = fields.Datetime(string=_("Activation Date"), readonly=True)
    deactivation_date = fields.Datetime(string=_("Deactivation Date"), readonly=True)

    @api.constrains("database_name")
    def _check_database_name(self):
        for tenant in self:
            if tenant.database_name and not tenant.database_name.isidentifier():
                raise ValidationError(
                    _(
                        "Database name must be a valid identifier (letters, numbers, underscores only)"
                    )
                )
            if tenant.database_name and len(tenant.database_name) > 63:
                raise ValidationError(
                    _("Database name must be less than 64 characters")
                )
            if tenant.database_name and tenant.database_name.lower() == "master":
                raise ValidationError(
                    _('Database name "master" is reserved for the super admin database')
                )

    @api.constrains("admin_email")
    def _check_admin_email(self):
        for tenant in self:
            if tenant.admin_email:
                import re

                pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
                if not re.match(pattern, tenant.admin_email):
                    raise ValidationError(_("Please enter a valid email address"))

    @api.depends("database_name")
    def _compute_user_count(self):
        for tenant in self:
            count = 0
            if tenant.database_name:
                try:
                    from odoo.modules.registry import Registry
                    # Ensure we get a fresh registry for the tenant database
                    db_registry = Registry(tenant.database_name)
                    with db_registry.cursor() as cr:
                        env = api.Environment(cr, SUPERUSER_ID, {})
                        count = env["res.users"].search_count([])
                except Exception as e:
                    _logger = logging.getLogger(__name__)
                    _logger.warning(
                        "Impossible de calculer le nombre d'utilisateurs pour la base %s : %s",
                        tenant.database_name,
                        e,
                    )
            tenant.user_count = count

    @api.depends("max_users")
    def _compute_user_limit_reached(self):
        for tenant in self:
            tenant.user_limit_reached = False

    # -----------------------------------------------------------------
    # Action serveur pour forcer le recompute du champ `user_count`
    # -----------------------------------------------------------------
    def action_recompute_user_count(self):
        """Recalculer le nombre d'utilisateurs pour tous les tenants."""
        for tenant in self.search([]):
            tenant._compute_user_count()
        # Recharger la vue afin de refléter les nouvelles valeurs
        return {"type": "ir.actions.client", "tag": "reload"}


    @api.depends("pack_id")
    def _compute_installed_modules(self):
        for tenant in self:
            if tenant.pack_id:
                tenant.installed_modules = tenant.pack_id.module_ids
            else:
                tenant.installed_modules = False

    def action_activate(self):
        self.ensure_one()
        if self.state != "draft":
            raise UserError(_("Only draft tenants can be activated"))

        if not self.pack_id:
            raise UserError(_("Please assign a pack before activation"))

        self.write(
            {
                "state": "active",
                "activation_date": fields.Datetime.now(),
            }
        )
        self._install_pack_modules()

    def action_suspend(self):
        self.ensure_one()
        if self.state != "active":
            raise UserError(_("Only active tenants can be suspended"))

        self.write(
            {
                "state": "suspended",
            }
        )
        # Deactivate the tenant's database to prevent any access
        self._deactivate_database()

    def action_reactivate(self):
        self.ensure_one()
        if self.state != "suspended":
            raise UserError(_("Only suspended tenants can be reactivated"))

        self.write(
            {
                "state": "active",
            }
        )
        self._reactivate_database()

    def action_archive(self):
        self.ensure_one()
        if self.state not in ["suspended", "draft"]:
            raise UserError(_("Only suspended or draft tenants can be archived"))

        self.write(
            {
                "state": "archived",
                "active": False,
                "deactivation_date": fields.Datetime.now(),
            }
        )

    def action_unarchive(self):
        """Revert an archived tenant to draft and reactivate it."""
        self.ensure_one()
        if self.state != "archived":
            raise UserError(_("Only archived tenants can be unarchived"))
        self.write(
            {
                "state": "draft",
                "active": True,
                "deactivation_date": False,
            }
        )

    def _deactivate_database(self):
        """Rename the tenant's database with a prefix to make it inaccessible.
        This is a simple way to mark the DB as inactive without deleting it.
        In a production environment you may prefer a proper deactivation
        mechanism provided by your hosting infrastructure.
        """
        if not self.database_name:
            return
        try:
            # Ensure the database exists
            if self.database_name not in list_dbs():
                return
            # If already prefixed with 'inactive_', do not add another prefix
            if self.database_name.startswith('inactive_'):
                # Already inactive; nothing to do
                return
            new_name = f"inactive_{self.database_name}"
            # Rename only if the target name does not already exist
            if new_name not in list_dbs():
                _logger = logging.getLogger(__name__)
                _logger.info(
                    "Renaming tenant database %s to %s",
                    self.database_name,
                    new_name,
                )
                exp_rename(self.database_name, new_name)
                # Update the record to keep track of the new name
                self.write({"database_name": new_name})
        except Exception as e:
            _logger = logging.getLogger(__name__)
            _logger.warning(
                "Failed to deactivate database %s: %s", self.database_name, e
            )

    def _reactivate_database(self):
        """Rename the tenant's database back to its original name to reactivate it.
        If the original database already exists, only update the record name.
        This method removes all leading 'inactive_' prefixes that may have been
        added during multiple suspensions.
        """
        if not self.database_name:
            return
        try:
            _logger = logging.getLogger(__name__)
            # Strip all leading 'inactive_' prefixes
            original_name = self.database_name
            while original_name.startswith('inactive_'):
                original_name = original_name[len('inactive_') :]
            if original_name == self.database_name:
                # No prefix to remove; nothing to do
                return
            if original_name not in list_dbs():
                _logger.info(
                    "Renaming tenant database %s back to %s",
                    self.database_name,
                    original_name,
                )
                exp_rename(self.database_name, original_name)
            else:
                _logger.warning(
                    "Original database %s already exists; keeping current (inactive) database as active.",
                    original_name,
                )
            # Update the tenant record to use the original (or stripped) name
            self.write({"database_name": original_name})
        except Exception as e:
            _logger = logging.getLogger(__name__)
            _logger.warning(
                "Failed to reactivate database %s: %s", self.database_name, e
            )

    def _install_pack_modules(self):
        self.ensure_one()
        if not self.pack_id:
            return

        modules_to_install = self.pack_id.module_ids

        for module in modules_to_install:
            if module.state != 'installed':
                module.button_install()

    def unlink(self):
        for tenant in self:
            if tenant.state == "active":
                raise UserError(
                    _("Cannot delete active tenants. Suspend or archive them first.")
                )
            # Drop the tenant's database if it exists
            if tenant.database_name:
                _logger = logging.getLogger(__name__)
                try:
                    exp_drop(tenant.database_name)
                except Exception as e:
                    _logger.error(
                        "Failed to drop database %s during tenant deletion: %s",
                        tenant.database_name,
                        e,
                    )
        return super(SaasTenant, self).unlink()

    @api.model_create_multi
    def create(self, vals_list):
        result = []
        for vals in vals_list:
            admin_password = vals.pop('admin_password', None)  # Remove from vals as it's not stored

            tenant = super(SaasTenant, self).create(vals)

            # If admin_password is provided, create the database automatically
            if admin_password and tenant.database_name:
                from odoo.service.db import exp_create_database, list_dbs

                # Check if database already exists
                existing_dbs = list_dbs()
                if tenant.database_name in existing_dbs:
                    # Database already exists, skip creation
                    pass
                else:
                    # Create the database
                    try:
                        exp_create_database(
                            tenant.database_name,
                            demo=False,
                            lang='fr_FR',
                            user_password=admin_password,
                            login=tenant.admin_email,
                            country_code='FR'
                        )
                        # -----------------------------------------------------------------
                        # Ensure the SaaS Tenant Guard module is NOT automatically installed
                        # in the newly created tenant database. Some Odoo setups may try to
                        # install all available modules, which leads to an import error
                        # (missing odoo.registry) for this module. We explicitly uninstall it
                        # if it appears as installed.
                        # -----------------------------------------------------------------
                        try:
                            from odoo import api, SUPERUSER_ID
                            from odoo.modules import registry as odoo_registry

                            tenant_registry = odoo_registry.Registry.new(tenant.database_name)
                            with tenant_registry.cursor() as cr:
                                env = api.Environment(cr, SUPERUSER_ID, {})
                                guard_mod = env["ir.module.module"].search([
                                    ("name", "=", "saas_tenant_guard"),
                                    ("state", "=", "installed"),
                                ])
                                if guard_mod:
                                    guard_mod.button_uninstall()
                        except Exception as e:
                            # Log the issue but do not prevent tenant creation
                            _logger = logging.getLogger(__name__)
                            _logger.warning(
                                "Failed to ensure saas_tenant_guard is not installed in tenant %s: %s",
                                tenant.database_name,
                                e,
                            )
                    except Exception as e:
                        tenant.unlink()  # Delete the tenant record if DB creation fails
                        raise UserError(_("Failed to create database: %s") % str(e))

                # Note: Module installation will be done manually by connecting to the new DB
                # and installing 'saas_tenant_guard' via Applications

            if tenant.pack_id:
                tenant._install_pack_modules()

            result.append(tenant)
        return self.browse([t.id for t in result])

    def write(self, vals):
        if "pack_id" in vals:
            new_pack_id = vals.get("pack_id")
            for tenant in self:
                if new_pack_id and tenant.state == "active":
                    raise UserError(
                        _("Cannot change pack for active tenant. Suspend first.")
                    )
        return super(SaasTenant, self).write(vals)

    def name_get(self):
        result = []
        for tenant in self:
            name = f"{tenant.name} ({tenant.database_name})"
            result.append((tenant.id, name))
        return result

    def action_create_tenant_wizard(self):
        return {
            "type": "ir.actions.act_window",
            "name": _("Create SaaS Tenant"),
            "res_model": "saas.create.tenant",
            "view_mode": "form",
            "view_type": "form",
            "target": "new",
        }

    def action_assign_pack_wizard(self):
        return {
            "type": "ir.actions.act_window",
            "name": _("Assign Pack to Tenant"),
            "res_model": "saas.assign.pack",
            "view_mode": "form",
            "view_type": "form",
            "target": "new",
            "context": {"default_tenant_id": self.id},
        }

    



