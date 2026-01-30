from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging
# Function to drop a PostgreSQL database for a tenant
from odoo.service.db import exp_drop
import logging
# Odoo provides a ``drop`` function to remove a database.


class SaasDeactivateTenant(models.TransientModel):
    _name = "saas.deactivate.tenant"
    _description = "SaaS Deactivate Tenant Wizard"

    tenant_id = fields.Many2one(
        "saas.tenant", string="Tenant", required=True, readonly=True
    )
    deactivation_reason = fields.Text(string="Deactivation Reason", required=True)
    archive_database = fields.Boolean(
        string="Archive Database",
        default=False,
        help="If checked, the tenant will be marked as archived",
    )

    user_count = fields.Integer(
        string="Current User Count", related="tenant_id.user_count", readonly=True
    )
    active_modules_count = fields.Integer(
        string="Active Modules Count",
        compute="_compute_active_modules_count",
        readonly=True,
    )

    # ---------------------------------------------------------------------
    # Default values
    # ---------------------------------------------------------------------
    @api.model
    def default_get(self, fields):
        """Automatically fill ``tenant_id`` when the wizard is opened from a
        tenant form.

        Odoo provides the ``active_id`` of the record that triggered the wizard
        in the context.  By reading this value we can set the required
        ``tenant_id`` field, which in turn populates the related read‑only fields
        (user count, active modules count, etc.).
        """
        res = super(SaasDeactivateTenant, self).default_get(fields)
        if "tenant_id" in fields:
            active_id = self.env.context.get("active_id")
            if active_id:
                res["tenant_id"] = active_id
        return res

    @api.depends("tenant_id")
    def _compute_active_modules_count(self):
        for wizard in self:
            if wizard.tenant_id and wizard.tenant_id.pack_id:
                wizard.active_modules_count = len(wizard.tenant_id.pack_id.module_ids)
            else:
                wizard.active_modules_count = 0

    def action_deactivate(self):
        """Deactivate a tenant.

        The wizard can perform two distinct actions depending on the
        ``archive_database`` flag:

        * **Suspend** – only allowed when the tenant is currently *active*.
        * **Archive** – allowed when the tenant is *suspended* or in *draft*
          state.  Archiving a tenant that is still active would first
          require it to be suspended.
        """
        self.ensure_one()

        # -----------------------------------------------------------------
        # Validation of the deactivation reason
        # -----------------------------------------------------------------
        if not self.deactivation_reason:
            raise UserError(_("Please provide a deactivation reason."))

        # -----------------------------------------------------------------
        # Determine which operation is requested and validate the tenant state
        # -----------------------------------------------------------------
        if self.archive_database:
            # Archiving is only allowed for suspended or draft tenants
            if self.tenant_id.state not in ("suspended", "draft"):
                raise UserError(
                    _(
                        "Only suspended or draft tenants can be archived."
                    )
                )
            # Archive the tenant record
            # Archive the tenant record first
            self.tenant_id.action_archive()
            # After archiving, drop the physical tenant database to stop it
            if self.tenant_id.database_name:
                _logger = logging.getLogger(__name__)
                try:
                    exp_drop(self.tenant_id.database_name)
                except Exception as e:
                    # Log the error but do not prevent the wizard from completing
                    _logger.error(
                        "Failed to drop tenant database %s during archive: %s",
                        self.tenant_id.database_name,
                        e,
                    )
        else:
            # Suspension is only allowed for active tenants
            if self.tenant_id.state != "active":
                raise UserError(_("Only active tenants can be suspended."))
            self.tenant_id.action_suspend()

        # -----------------------------------------------------------------
        # Record the deactivation reason in the tenant notes
        # -----------------------------------------------------------------
        new_notes = self.tenant_id.notes or ""
        if new_notes:
            new_notes += "\n\n"
        new_notes += (
            f"Deactivated on {fields.Datetime.now()}: {self.deactivation_reason}"
        )
        self.tenant_id.write({"notes": new_notes})

        # -----------------------------------------------------------------
        # Return a client notification
        # -----------------------------------------------------------------
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Tenant Deactivated"),
                "message": _('Tenant "%s" has been deactivated.')
                % (self.tenant_id.name,),
                "type": "success",
                "sticky": False,
            },
        }
