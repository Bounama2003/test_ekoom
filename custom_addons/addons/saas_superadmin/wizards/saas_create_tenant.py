from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.service.db import exp_create_database
from odoo.api import Environment
from odoo import SUPERUSER_ID
import odoo


class SaasCreateTenant(models.TransientModel):
    _name = "saas.create.tenant"
    _description = "SaaS Create Tenant Wizard"

    name = fields.Char(string="Tenant Name", required=True)
    database_name = fields.Char(
        string="Database Name",
        required=True,
        help="The name of the PostgreSQL database for this tenant",
    )
    company_name = fields.Char(string="Company Name", required=True)
    admin_email = fields.Char(string="Admin Email", required=True)
    admin_password = fields.Char(
        string="Admin Password",
        required=True,
        default="admin",
        help="Password for the admin user in the new tenant database",
    )
    admin_phone = fields.Char(string="Admin Phone")
    pack_id = fields.Many2one(
        "saas.pack",
        string="Business Pack",
        required=True,
        domain=[("active", "=", True)],
    )
    max_users = fields.Integer(string="Max Users", default=100, required=True)
    notes = fields.Text(string="Notes")

    @api.constrains("database_name")
    def _check_database_name(self):
        for wizard in self:
            if wizard.database_name and not wizard.database_name.isidentifier():
                raise ValidationError(
                    _(
                        "Database name must be a valid identifier (letters, numbers, underscores only)"
                    )
                )
            if wizard.database_name and len(wizard.database_name) > 63:
                raise ValidationError(
                    _("Database name must be less than 64 characters")
                )
            if wizard.database_name and wizard.database_name.lower() == "master":
                raise ValidationError(
                    _('Database name "master" is reserved for the super admin database')
                )

    @api.constrains("admin_email")
    def _check_admin_email(self):
        for wizard in self:
            if wizard.admin_email:
                import re

                pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
                if not re.match(pattern, wizard.admin_email):
                    raise ValidationError(_("Please enter a valid email address"))

    @api.constrains("admin_password")
    def _check_admin_password(self):
        for wizard in self:
            if wizard.admin_password and len(wizard.admin_password) < 6:
                raise ValidationError(_("Admin password must be at least 6 characters long"))
    def _check_max_users(self):
        for wizard in self:
            if wizard.max_users <= 0:
                raise ValidationError(_("Max users must be greater than 0"))
            if wizard.max_users > 100:
                raise ValidationError(_("Max users cannot exceed 100 per tenant"))

    def action_create_tenant(self):
        self.ensure_one()

        existing_tenant = self.env["saas.tenant"].search(
            [("database_name", "=", self.database_name)], limit=1
        )

        if existing_tenant:
            raise UserError(_("A tenant with this database name already exists."))

        tenant = self.env["saas.tenant"].create(
            {
                "name": self.name,
                "database_name": self.database_name,
                "company_name": self.company_name,
                "admin_email": self.admin_email,
                "admin_phone": self.admin_phone,
                "pack_id": self.pack_id.id,
                "max_users": self.max_users,
                "notes": self.notes,
                "state": "draft",
            }
        )

        # Créer la base de données
        try:
            exp_create_database(
                self.database_name,
                demo=False,
                lang='fr_FR',
                user_password=self.admin_password,
                login=self.admin_email,
                country_code='FR'
            )
        except Exception as e:
            tenant.unlink()  # Supprimer le tenant si la DB échoue
            raise UserError(_("Failed to create database: %s") % str(e))

        # Skipping installation of saas_tenant_guard module as per requirement
        # (Database is created without installing the guard module)

        return {
            "type": "ir.actions.act_window",
            "name": _("Tenant Created"),
            "res_model": "saas.tenant",
            "res_id": tenant.id,
            "view_mode": "form",
            "view_type": "form",
            "target": "current",
        }
