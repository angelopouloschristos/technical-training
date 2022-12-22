from datetime import timedelta

from odoo import api, models, fields


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_confirm(self):
        #partner = self.partner_id

        #if partner.max_amount and self.amount_total > partner.max_amount:
        #    raise Exception("Le montant total de la commande dépasse le montant maximal de validation du partenaire.")
        max_amount = self.user_has_required_level()

        if self.amount_total <= max_amount:
            for line in self.order_line:
                employee = line.employee_id
                if not employee.user_id:
                    partner = self.env['res.partner'].create({
                        'name': employee.name,
                    })
                else:
                    partner = employee.user_id.partner_id
                event = self.env['calendar.event'].create({
                    'name': 'Formation Odoo',
                    'start': line.training_date,
                    'stop': line.training_date + timedelta(hours=8),
                    'allday': True,
                    'partner_ids': [(4, partner.id)],
                })

                return super(SaleOrder, self).action_confirm()
        else:
            return self.message_post(body="Le montant total de la commande dépasse le montant maximal de validation du partenaire.")



    def user_has_required_level(self):
        # Récupération de l'utilisateur actuel
        user = self.env.user
        default_max_amount = 500
        # Récupération des groupes de l'utilisateur
        groups = user.groups_id

        # Initialisation du niveau de gestionnaire de l'utilisateur à 0
        maxamountapproval = default_max_amount

        # Vérification du niveau de gestionnaire de l'utilisateur
        for group in groups:
            if group.max_amount:
                maxamountapproval = group.max_amount
                #user_level = max(user_level, group.max_amount)

        # Comparaison du niveau de gestionnaire de l'utilisateur au niveau requis
        #return user_level >= required_level
        return maxamountapproval


    def action_request_approval(self):
        # Envoi d'un message à l'utilisateur pour lui demander d'obtenir l'approbation
        self.message_post(body="La commande nécessite une approbation de la part d'un gestionnaire de niveau supérieur.")

        # Renvoi d'une action pour afficher la commande et lui demander l'approbation
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'current',
        }

