# -*- coding: utf-8 -*-
"""Model to store dynamic SaaS pack categories (niches).

This replaces the static ``Selection`` field on ``saas.pack`` with a
``Many2one`` relationship, allowing administrators to create, edit and
remove categories from the master interface.
"""

from odoo import models, fields, _


class SaasPackCategory(models.Model):
    _name = "saas.pack.category"
    _description = "SaaS Pack Category"
    _order = "name asc"

    name = fields.Char(string="Category", required=True, translate=True)
    code = fields.Char(string="Code", required=True, copy=False)
    description = fields.Text(string="Description")
    active = fields.Boolean(string="Active", default=True)
