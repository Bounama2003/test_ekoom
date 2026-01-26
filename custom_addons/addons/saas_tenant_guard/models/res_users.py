from odoo import models, api, _
from odoo.exceptions import UserError, AccessError


class ResUsers(models.Model):
    _inherit = "res.users"

    @api.model_create_multi
    def create(self, vals_list):
        # Determine relevant group IDs once for efficiency
        internal_group = self.env.ref('base.group_user', raise_if_not_found=False)
        system_group = self.env.ref('base.group_system', raise_if_not_found=False)
        internal_group_id = internal_group.id if internal_group else None
        system_group_id = system_group.id if system_group else None

        for vals in vals_list:
            # Enforce total user limit for the tenant
            self._check_user_creation_limit()
            # Enforce only one internal user per tenant if the new user is internal
            if internal_group_id and self._is_internal_user(vals, internal_group_id):
                self._check_internal_user_limit(internal_group_id)
            # Prevent creation of a system administrator user under any circumstance
            if system_group_id and self._has_group_in_vals(vals, system_group_id):
                raise UserError(_("Creating a system administrator is not allowed for tenant users."))
        return super(ResUsers, self).create(vals_list)

    def _is_internal_user(self, vals, internal_group_id):
        """Return True if the creation values assign the internal user group.

        The ``groups_id`` field uses the standard Odoo many2many command format.
        We inspect the commands to see if the internal group ID is being added.
        """
        groups_cmd = vals.get('groups_id')
        if not groups_cmd:
            return False
        # groups_cmd is a list of commands, each command is a tuple/list
        for cmd in groups_cmd:
            # Command 6: replace with list of IDs
            if isinstance(cmd, (list, tuple)) and cmd and cmd[0] == 6:
                # cmd[2] is the list of IDs to set
                if internal_group_id in cmd[2]:
                    return True
            # Command 4: add a single ID
            if isinstance(cmd, (list, tuple)) and cmd and cmd[0] == 4:
                if cmd[1] == internal_group_id:
                    return True
            # Command 3: remove a single ID – not relevant for creation
        return False

    def _has_group_in_vals(self, vals, group_id):
        """Utility to check if a many2many command list adds a specific group.

        Used for detecting attempts to assign the system admin group during record creation.
        This method name avoids colliding with Odoo's internal ``_has_group`` implementation.
        """
        groups_cmd = vals.get('groups_id')
        if not groups_cmd:
            return False
        for cmd in groups_cmd:
            if isinstance(cmd, (list, tuple)) and cmd:
                # Command 6: replace with list of IDs
                if cmd[0] == 6 and group_id in cmd[2]:
                    return True
                # Command 4: add a single ID
                if cmd[0] == 4 and cmd[1] == group_id:
                    return True
        return False

    def _check_internal_user_limit(self, internal_group_id):
        """Raise an error if an internal user already exists in the tenant.

        Tenants are isolated databases, so ``search_count`` will only count users
        within the current tenant database.
        """
        internal_user_count = self.search_count([('groups_id', 'in', [internal_group_id])])
        if internal_user_count >= 1:
            raise UserError(
                _(
                    "Only one internal user is allowed per tenant. "
                    "An internal user already exists (count: %s)."
                ) % internal_user_count
            )

    @api.model
    def _check_user_creation_limit(self):
        param_max_users = "saas_tenant_guard.max_users"
        max_users = (
            self.env["ir.config_parameter"].sudo().get_param(param_max_users, "100")
        )

        try:
            max_users = int(max_users)
        except (ValueError, TypeError):
            max_users = 100

        current_user_count = self.search_count([])

        if current_user_count >= max_users:
            raise UserError(
                _(
                    "User limit reached.\n\n"
                    "This tenant is limited to %s users maximum.\n"
                    "Current users: %s\n\n"
                    "Contact your SaaS provider to increase your user limit."
                )
                % (max_users, current_user_count)
            )

    @api.model
    def check_user_limit_reached(self):
        param_max_users = "saas_tenant_guard.max_users"
        max_users = (
            self.env["ir.config_parameter"].sudo().get_param(param_max_users, "100")
        )

        try:
            max_users = int(max_users)
        except (ValueError, TypeError):
            max_users = 100

        current_user_count = self.search_count([])

        return {
            "limit_reached": current_user_count >= max_users,
            "current_users": current_user_count,
            "max_users": max_users,
        }

    @api.model
    def get_user_limit_info(self):
        param_max_users = "saas_tenant_guard.max_users"
        max_users = (
            self.env["ir.config_parameter"].sudo().get_param(param_max_users, "100")
        )

        try:
            max_users = int(max_users)
        except (ValueError, TypeError):
            max_users = 100

        current_user_count = self.search_count([])

        return {
            "current_users": current_user_count,
            "max_users": max_users,
            "available_users": max(0, max_users - current_user_count),
            "limit_reached": current_user_count >= max_users,
        }
