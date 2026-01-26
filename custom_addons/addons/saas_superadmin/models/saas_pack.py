from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class SaasPack(models.Model):
    _name = "saas.pack"
    _description = "SaaS Business Pack"
    _order = "name asc"

    name = fields.Char(string="Pack Name", required=True, translate=True)
    code = fields.Char(string="Pack Code", required=True, copy=False)
    description = fields.Text(string="Description", translate=True)
    active = fields.Boolean(string="Active", default=True)

    module_ids = fields.Many2many(
        "ir.module.module",
        "saas_pack_module_rel",
        "pack_id",
        "module_id",
        string="Included Modules",
    )

    tenant_ids = fields.One2many("saas.tenant", "pack_id", string="Tenants")
    tenant_count = fields.Integer(
        string="Tenant Count", compute="_compute_tenant_count", store=True
    )

    # Replace static selection with a dynamic many2one to allow user‑defined categories (niches)
    category_id = fields.Many2one(
        "saas.pack.category",
        string="Category",
        required=False,
        ondelete="restrict",
        default=lambda self: self.env.ref('saas_superadmin.category_default', raise_if_not_found=False).id,
    )

    is_predefined = fields.Boolean(string="Is Predefined", default=False)
    sequence = fields.Integer(string="Sequence", default=10)

    @api.constrains("code")
    def _check_code_unique(self):
        for pack in self:
            if pack.code:
                existing = self.search(
                    [("code", "=", pack.code), ("id", "!=", pack.id)], limit=1
                )
                if existing:
                    raise ValidationError(_("Pack code must be unique"))

    @api.depends("tenant_ids")
    def _compute_tenant_count(self):
        for pack in self:
            pack.tenant_count = len(pack.tenant_ids)

    def action_view_tenants(self):
        self.ensure_one()
        return {
            "name": _("Tenants"),
            "type": "ir.actions.act_window",
            "res_model": "saas.tenant",
            "view_mode": "list,form",
            "domain": [("pack_id", "=", self.id)],
            "context": {"default_pack_id": self.id},
        }

    def action_view_modules(self):
        self.ensure_one()
        return {
            "name": _("Included Modules"),
            "type": "ir.actions.act_window",
            "res_model": "ir.module.module",
            "view_mode": "list",
            "domain": [("id", "in", self.module_ids.ids)],
            "context": {},
        }

    @api.model
    def get_predefined_packs(self):
        return self.search([("is_predefined", "=", True)])

    def unlink(self):
        for pack in self:
            if pack.tenant_ids:
                raise UserError(_("Cannot delete pack with existing tenants."))
        return super(SaasPack, self).unlink()

    def name_get(self):
        result = []
        for pack in self:
            name = f"[{pack.code}] {pack.name}"
            result.append((pack.id, name))
        return result
