from odoo import fields, models

class ResPartner(models.Model):
    _inherit = 'res.partner'
    approval_amount = fields.Float(string="Approval Amount")
