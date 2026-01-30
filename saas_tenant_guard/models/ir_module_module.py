"""Enforce SaaS pack module installation restrictions.

This model overrides the standard install buttons for ``ir.module.module``.
It checks the ``saas_tenant_guard.allowed_modules`` configuration
parameter (populated when a pack is assigned) and raises a ``UserError``
if a tenant admin tries to install a module that is not part of the pack.
"""

from odoo import models, api, _
from odoo.exceptions import UserError


class IrModuleModule(models.Model):
    _inherit = "ir.module.module"

    @api.model
    def _get_allowed_modules(self):
        """Return a set of technical module names allowed for the current tenant.

        The configuration is stored in ``ir.config_parameter`` under the key
        ``saas_tenant_guard.allowed_modules`` as a comma‑separated list.
        """
        param = "saas_tenant_guard.allowed_modules"
        allowed = self.env["ir.config_parameter"].sudo().get_param(param, "")
        return {name.strip() for name in allowed.split(",") if name.strip()}

    def _check_install_permission(self):
        """Raise ``UserError`` if the current user is a SaaS tenant admin and the
        module is not in the allowed list.
        """
        if self.env.user.has_group("saas_tenant_guard.group_saas_tenant_admin"):
            allowed = self._get_allowed_modules()
            if allowed and self.name not in allowed:
                raise UserError(
                    _(
                        "You cannot install the module '%s' because it is not part of the pack assigned to your tenant."
                    )
                    % self.name
                )

    # ---------------------------------------------------------------------
    # Override the two install entry points used by the UI
    # ---------------------------------------------------------------------
    def button_install(self):
        for module in self:
            module._check_install_permission()
            module._install_external_dependencies()
        return super(IrModuleModule, self).button_install()

    def button_immediate_install(self):
        for module in self:
            module._check_install_permission()
            module._install_external_dependencies()
        return super(IrModuleModule, self).button_immediate_install()

    def _install_external_dependencies(self):
        """Override Odoo's internal method to auto‑install missing Python deps.

        Odoo's original ``ir.module.module._install_external_dependencies`` checks
        the ``external_dependencies`` manifest entry and raises a ``UserError``
        if a required Python package is not present.  We replace that behaviour
        by attempting to install the missing packages via ``pip`` before delegating
        to the original implementation (which will simply pass when the packages
        are now available).
        """
        # Retrieve the manifest‑declared external dependencies (may be empty).
        deps = getattr(self, "external_dependencies", {}) or {}
        python_deps = deps.get("python", [])
        # No external Python dependencies declared – nothing to do.
        if not python_deps:
            return True

        import importlib
        import subprocess
        import sys

        import logging
        _logger = logging.getLogger(__name__)
        for pkg in python_deps:
            try:
                importlib.import_module(pkg)
            except ImportError:
                # Try to install the exact package name.
                try:
                    # Use pip via the same interpreter; add --quiet to reduce output.
                    subprocess.check_call([
                        sys.executable,
                        "-m",
                        "pip",
                        "install",
                        "--quiet",
                        pkg,
                    ])
                    importlib.import_module(pkg)
                    _logger.info("Successfully installed external dependency %s", pkg)
                except Exception as e:
                    # Attempt fallback for common typo "phonenumber" -> "phonenumbers"
                    fallback = "phonenumbers" if pkg.lower() == "phonenumber" else None
                    if fallback:
                        try:
                            subprocess.check_call([
                                sys.executable,
                                "-m",
                                "pip",
                                "install",
                                "--quiet",
                                fallback,
                            ])
                            importlib.import_module(fallback)
                            _logger.info("Successfully installed fallback external dependency %s", fallback)
                        except Exception as e2:
                            _logger.error(
                                "Failed to install external dependency %s (fallback %s): %s",
                                pkg,
                                fallback,
                                e2,
                            )
                            raise UserError(
                                _(
                                    "Unable to install required Python package '%s' (or fallback '%s')."
                                    % (pkg, fallback)
                                )
                            )
                    else:
                        _logger.error("Failed to install external dependency %s: %s", pkg, e)
                        raise UserError(
                            _(f"Unable to install required Python package '{pkg}'.")
                        )

        # Dependencies installed – return success.
        return True
