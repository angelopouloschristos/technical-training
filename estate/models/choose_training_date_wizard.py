from odoo import api, fields, models, _


class ChooseTrainingDateWizard(models.TransientModel):
    _inherit = 'choose.training.date.wizard'

    start_date = fields.Date(string='Start Date', required=True)
    end_date = fields.Date(string='End Date', required=True)

    def confirm_dates(self):
        for line in self.order_id.order_line:
            line.write({'training_date': self.start_date})

    def open_choose_training_date_wizard(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'choose.training.date.wizard',  # Correction ici
            'view_mode': 'form',
            'target': 'new',
        }
