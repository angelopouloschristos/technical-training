from odoo import models, fields, api


class ChooseTrainingDateWizard(models.TransientModel):
    _name = 'choose.training.date.wizard'

    training_date = fields.Date(string='Training Date', required=True)

    @api.multi
    def confirm(self):
        # Récupération de la ligne de commande sélectionnée
        active_id = self._context.get('active_id')
        order_line = self.env['sale.order.line'].browse(active_id)

        # Mise à jour de la date de formation de la ligne de commande
        order_line.write({'training_date': self.training_date})
