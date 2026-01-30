from odoo import models, fields, api, _
from odoo.exceptions import UserError


class SaasChangePack(models.TransientModel):
    _name = "saas.change.pack"
    _description = "SaaS Change Pack Wizard"

    tenant_id = fields.Many2one(
        "saas.tenant", string="Tenant", required=True, readonly=True
    )
    current_pack_id = fields.Many2one(
        "saas.pack", string="Current Pack", related="tenant_id.pack_id", readonly=True
    )
    new_pack_id = fields.Many2one(
        "saas.pack", string="New Pack", required=True, domain=[("active", "=", True)]
    )

    current_modules = fields.Many2many(
        "ir.module.module",
        string="Current Modules",
        compute="_compute_modules",
        readonly=True,
    )
    new_modules = fields.Many2many(
        "ir.module.module",
        string="New Modules",
        compute="_compute_modules",
        readonly=True,
    )

    # ---------------------------------------------------------------------
    # Default values
    # ---------------------------------------------------------------------
    @api.model
    def default_get(self, fields):
        """Populate ``tenant_id`` automatically when the wizard is opened
        from a tenant form.

        Odoo passes the ``active_id`` of the record that triggered the
        wizard in the context.  By reading this value we can set the
        ``tenant_id`` field so that the related ``current_pack_id`` and the
        computed module lists are correctly filled.
        """
        res = super(SaasChangePack, self).default_get(fields)
        if "tenant_id" in fields:
            active_id = self.env.context.get("active_id")
            if active_id:
                res["tenant_id"] = active_id
        return res

    modules_to_add = fields.Many2many(
        "ir.module.module",
        string="Modules to Add",
        compute="_compute_modules_diff",
        readonly=True,
    )
    modules_to_remove = fields.Many2many(
        "ir.module.module",
        string="Modules to Remove",
        compute="_compute_modules_diff",
        readonly=True,
    )

    @api.depends("tenant_id", "new_pack_id")
    def _compute_modules(self):
        for wizard in self:
            if wizard.tenant_id.pack_id:
                wizard.current_modules = wizard.tenant_id.pack_id.module_ids
            else:
                wizard.current_modules = False

            if wizard.new_pack_id:
                wizard.new_modules = wizard.new_pack_id.module_ids
            else:
                wizard.new_modules = False

    @api.depends("current_modules", "new_modules")
    def _compute_modules_diff(self):
        for wizard in self:
            if wizard.current_modules and wizard.new_modules:
                modules_to_add = wizard.new_modules - wizard.current_modules
                modules_to_remove = wizard.current_modules - wizard.new_modules
                wizard.modules_to_add = modules_to_add.ids if modules_to_add else False
                wizard.modules_to_remove = (
                    modules_to_remove.ids if modules_to_remove else False
                )
            else:
                wizard.modules_to_add = False
                wizard.modules_to_remove = False

    def action_change_pack(self):
        self.ensure_one()

        if self.tenant_id.state == "active":
            raise UserError(
                _("Cannot change pack for active tenant. Suspend the tenant first.")
            )

        if self.tenant_id.state == "archived":
            raise UserError(_("Cannot change pack for archived tenant."))

        if self.new_pack_id.id == self.current_pack_id.id:
            raise UserError(_("New pack is the same as the current pack."))

        self.tenant_id.write(
            {
                "pack_id": self.new_pack_id.id,
            }
        )

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Pack Changed"),
                "message": _('Pack has been changed from "%s" to "%s".')
                % (self.current_pack_id.name, self.new_pack_id.name),
                "type": "success",
                "sticky": False,
            },
        }
