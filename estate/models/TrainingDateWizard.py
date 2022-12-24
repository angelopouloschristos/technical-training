from odoo import api, models, fields


class TrainingDateWizard(models.TransientModel):
    _name = 'training.date.wizard'
    _description = 'Wizard to select the training date'

    training_date = fields.Date(string='Training Date')

    def default_get(self, fields):
        # Récupération de la ligne de commande en cours
        order_line = self.env['sale.order.line'].browse(self._context.get('active_id'))

        # Initialisation des valeurs par défaut du champ "training_date"
        default_values = {
            'training_date': order_line.training_date,
        }
        return default_values

    def choose_training_date(self):
        # Récupération de la ligne de commande en cours
        order_line = self.env['sale.order.line'].browse(self._context.get('active_id'))

        # Mise à jour de la date de formation de la ligne de commande avec la date sélectionnée dans l'assistant
        order_line.write({'training_date': self.training_date})
