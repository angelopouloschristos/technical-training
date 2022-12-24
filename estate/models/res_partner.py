from odoo import fields, models

class ResPartner(models.Model):
    _inherit = 'res.partner'
    max_amount = fields.Float(string="Max Price to be Approved")
    approved_orders_count = fields.Integer(string="Approved Orders Count")