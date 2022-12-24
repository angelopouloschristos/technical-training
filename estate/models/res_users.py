from odoo import fields, models


class ResUsers(models.Model):
    _inherit = 'res.users'
    approved_orders_count = fields.Integer(string="Approved Orders Count")
