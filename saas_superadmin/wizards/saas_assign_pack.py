from odoo import models, fields, api, _
from odoo.exceptions import UserError


class SaasAssignPack(models.TransientModel):
    _name = "saas.assign.pack"
    _description = "SaaS Assign Pack Wizard"

    tenant_id = fields.Many2one(
        "saas.tenant", string="Tenant", required=True, readonly=True
    )
    pack_id = fields.Many2one(
        "saas.pack",
        string="Business Pack",
        required=True,
        domain=[("active", "=", True)],
    )
    current_pack_id = fields.Many2one(
        "saas.pack", string="Current Pack", related="tenant_id.pack_id", readonly=True
    )
    modules_to_install = fields.Many2many(
        "ir.module.module",
        string="Modules to Install",
        compute="_compute_modules_to_install",
        readonly=True,
    )

    @api.model
    def default_get(self, fields):
        res = super(SaasAssignPack, self).default_get(fields)
        if 'tenant_id' in fields:
            active_id = self.env.context.get('active_id')
            if active_id:
                res['tenant_id'] = active_id
        return res

    @api.depends("pack_id")
    def _compute_modules_to_install(self):
        for wizard in self:
            if wizard.pack_id:
                wizard.modules_to_install = wizard.pack_id.module_ids
            else:
                wizard.modules_to_install = False

    def action_assign_pack(self):
        self.ensure_one()

        if self.tenant_id.state == "active":
            raise UserError(
                _("Cannot assign pack to active tenant. Suspend the tenant first.")
            )

        if self.tenant_id.state in ["archived"]:
            raise UserError(_("Cannot assign pack to archived tenant."))

        # Assign the pack to the tenant record in the master database
        self.tenant_id.write({"pack_id": self.pack_id.id})

        # -----------------------------------------------------------------
        # Propagate allowed modules to the tenant's own database via config
        # -----------------------------------------------------------------
        tenant_db = self.tenant_id.database_name
        if tenant_db:
            # Build a comma‑separated list of technical module names belonging to the pack
            allowed_modules = ",".join(self.pack_id.module_ids.mapped("name"))
            # Load the registry for the tenant database and write the config params
            from odoo.modules import registry as odoo_registry
            from odoo import SUPERUSER_ID, api

            tenant_registry = odoo_registry.Registry.new(tenant_db)
            with tenant_registry.cursor() as cr:
                env_tenant = api.Environment(cr, SUPERUSER_ID, {})
                env_tenant["ir.config_parameter"].sudo().set_param(
                    "saas_tenant_guard.allowed_modules", allowed_modules
                )
                # Also store the pack id for reference (optional)
                env_tenant["ir.config_parameter"].sudo().set_param(
                    "saas_tenant_guard.pack_id", str(self.pack_id.id)
                )

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Pack Assigned"),
                "message": _('Pack "%s" has been assigned to tenant "%s".')
                % (self.pack_id.name, self.tenant_id.name),
                "type": "success",
                "sticky": False,
            },
        }
