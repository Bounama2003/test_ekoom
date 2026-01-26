from odoo import models, fields, api, _
from odoo.exceptions import AccessError


class IrConfigParameter(models.Model):
    _inherit = "ir.config_parameter"

    def write(self, vals):
        for record in self:
            if record.key.startswith(
                "saas_tenant_guard."
            ) and not self.env.user.has_group("saas_superadmin.group_saas_superadmin"):
                raise AccessError(_("Only Super Admin can modify SaaS parameters"))
        return super(IrConfigParameter, self).write(vals)

    def unlink(self):
        for record in self:
            if record.key.startswith(
                "saas_tenant_guard."
            ) and not self.env.user.has_group("saas_superadmin.group_saas_superadmin"):
                raise AccessError(_("Only Super Admin can delete SaaS parameters"))
        return super(IrConfigParameter, self).unlink()
