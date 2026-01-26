from odoo import models, fields, api, _
from odoo.exceptions import AccessError


class SaasTenantConfig(models.TransientModel):
    _name = "saas.tenant.config"
    _description = "SaaS Tenant Configuration (Internal)"
    _auto = False
    _log_access = True

    tenant_pack_id = fields.Integer(string="Tenant Pack ID", readonly=True)
    tenant_pack_name = fields.Char(string="Tenant Pack Name", readonly=True)
    allowed_modules = fields.Text(string="Allowed Modules", readonly=True)
    max_users = fields.Integer(string="Max Users", readonly=True)
    is_active = fields.Boolean(string="Is Active", readonly=True)

    @api.model
    def get_config(self):
        param_pack_id = "saas_tenant_guard.pack_id"
        param_allowed_modules = "saas_tenant_guard.allowed_modules"
        param_max_users = "saas_tenant_guard.max_users"
        param_is_active = "saas_tenant_guard.is_active"

        pack_id = self.env["ir.config_parameter"].sudo().get_param(param_pack_id, "")
        allowed_modules = (
            self.env["ir.config_parameter"].sudo().get_param(param_allowed_modules, "")
        )
        max_users = (
            self.env["ir.config_parameter"].sudo().get_param(param_max_users, "100")
        )
        is_active = (
            self.env["ir.config_parameter"].sudo().get_param(param_is_active, "True")
        )

        try:
            pack_id = int(pack_id)
        except (ValueError, TypeError):
            pack_id = 0

        try:
            max_users = int(max_users)
        except (ValueError, TypeError):
            max_users = 100

        is_active = is_active.lower() in ["true", "1", "yes", "on"]

        # The ``saas.pack`` model is not installed in tenant databases (only the
        # ``saas_tenant_guard`` module is present).  Accessing it would raise a
        # ``KeyError``.  We therefore skip the lookup and simply return the pack
        # identifier without a name.
        pack_name = ""
        if pack_id:
            # Attempt to fetch the pack name only if the model exists (e.g. in
            # the master DB).  In tenant DB the model is absent, so we ignore it.
            if "saas.pack" in self.env.registry.models:
                pack = self.env["saas.pack"].sudo().search([("id", "=", pack_id)], limit=1)
                if pack:
                    pack_name = pack.name

        return {
            "tenant_pack_id": pack_id,
            "tenant_pack_name": pack_name,
            "allowed_modules": allowed_modules,
            "max_users": max_users,
            "is_active": is_active,
        }

    @api.model
    def set_config(self, pack_id, allowed_modules, max_users=100):
        param_pack_id = "saas_tenant_guard.pack_id"
        param_allowed_modules = "saas_tenant_guard.allowed_modules"
        param_max_users = "saas_tenant_guard.max_users"
        param_is_active = "saas_tenant_guard.is_active"

        self.env["ir.config_parameter"].sudo().set_param(param_pack_id, pack_id or "")
        self.env["ir.config_parameter"].sudo().set_param(
            param_allowed_modules, allowed_modules or ""
        )
        self.env["ir.config_parameter"].sudo().set_param(param_max_users, max_users)
        self.env["ir.config_parameter"].sudo().set_param(param_is_active, "True")

        return True

    @api.model
    def clear_config(self):
        param_pack_id = "saas_tenant_guard.pack_id"
        param_allowed_modules = "saas_tenant_guard.allowed_modules"
        param_max_users = "saas_tenant_guard.max_users"
        param_is_active = "saas_tenant_guard.is_active"

        self.env["ir.config_parameter"].sudo().set_param(param_is_active, "False")

        return True
