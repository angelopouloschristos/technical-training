from odoo import api, fields, models, _


class ChooseTrainingDateWizard(models.TransientModel):
    name = 'choose.training.date.wizard'

    start_date = fields.Date(string='Start Date', required=True)
    end_date = fields.Date(string='End Date', required=True)

    def confirm_dates(self):
        for line in self.order_id.order_line:
            line.write({'training_date': self.start_date})
