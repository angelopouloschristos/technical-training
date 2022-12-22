from datetime import timedelta

from odoo import api, models, fields


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_confirm(self):
        partner = self.partner_id
        if partner.max_amount and self.amount_total > partner.max_amount:
            raise Exception("Le montant total de la commande dépasse le montant maximal de validation du partenaire.")

        if self.amount_total <= 500:
            # Aucune approbation nécessaire
            pass
        elif self.amount_total > 500 and self.amount_total <= 2000:
            # Les gestionnaires de niveau 1 et supérieur peuvent confirmer
            if not self.user_has_required_level(1):
                return self.action_request_approval()
        elif self.amount_total > 2000 and self.amount_total <= 5000:
            # Les gestionnaires de niveau 2 et supérieur peuvent confirmer
            if not self.user_has_required_level(2):
                return self.action_request_approval()
        elif self.amount_total > 5000:
            # Les gestionnaires de niveau 3 et supérieur peuvent confirmer
            if not self.user_has_required_level(3):
                return self.action_request_approval()

        res = super(SaleOrder, self).action_confirm()

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

        return res


    def user_has_required_level(self, required_level):
        # Récupération de l'utilisateur actuel
        user = self.env.user

        # Récupération des groupes de l'utilisateur
        groups = user.groups_id

        # Initialisation du niveau de gestionnaire de l'utilisateur à 0
        user_level = 0

        # Vérification du niveau de gestionnaire de l'utilisateur
        for group in groups:
            if group.max_amount:
                user_level = max(user_level, group.max_amount)

        # Comparaison du niveau de gestionnaire de l'utilisateur au niveau requis
        return user_level >= required_level


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

