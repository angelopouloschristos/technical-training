from odoo import fields, models, api


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    training_date = fields.Date(string="Date de formation")
    employee_id = fields.Many2one('hr.employee', string="Employé")
