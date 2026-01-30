from odoo import models, fields

class SaasPackModule(models.Model):
    _name = "saas.pack.module"
    _description = "SaaS Pack Module"

    name = fields.Char(string="Module Name", required=True)
    pack_id = fields.Many2one("saas.pack", string="Pack", required=True)
