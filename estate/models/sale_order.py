from datetime import timedelta

from odoo import api, models, fields


##version fonctionnel
class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_confirm(self):
        # Récupération du partenaire associé à la commande en cours
        partner = self.partner_id
        max_amount = self.user_has_required_level()

        # Vérification que le montant total de la commande ne dépasse pas le montant maximal de validation du partenaire
        if self.amount_total <= max_amount and self.amount_total <= partner.max_amount or partner.max_amount is None:
            for line in self.order_line:
                employee = line.employee_id
                if not employee.user_id:
                    partner = self.env['res.partner'].create({
                        'name': employee.name,
                    })
                else:
                    partner = employee.user_id.partner_id
                # Création de l'évènement récurrent chaque année à la même date
                event = self.env['calendar.event'].create({
                    'name': 'Formation Odoo',
                    'start': line.training_date,
                    'stop': line.training_date + timedelta(hours=8),
                    'allday': True,
                    'partner_ids': [(4, partner.id)],
                    'rrule': 'FREQ=YEARLY;INTERVAL=1',
                })

            self.env.user.approved_orders_count += 1

            self.message_post(body="La commande a été approuvée par %s" % self.env.user.name)

            # Confirmation de la commande
            return super(SaleOrder, self).action_confirm()

        else:
            self.message_post(
                body="La commande nécessite une approbation de la part d'un gestionnaire de niveau supérieur.")

            # Sélection du gestionnaire avec le moins d'approbations en attente d'assignation (optionnel)
            manager = self.select_manager()
            if not manager:
                return

            # Création d'une activité pour le gestionnaire sélectionné
            self.activity_schedule(
                'mail.activity_data_todo',
                user_id=manager.id,
                note="Demande d'approbation de la commande %s" % self.name,
            )

            # Envoi d'un message à l'utilisateur pour lui signaler que la demande d'approbation a été envoyée au gestionnaire
            self.message_post(
                body="La demande d'approbation de la commande a été envoyée au gestionnaire %s" % manager.name)
            # Renvoi d'une action pour afficher la commande et lui demander l'approbation
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'sale.order',
                'res_id': self.id,
                'view_mode': 'form',
                'target': 'current',
            }

        # ... autres méthodes ...

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
                # user_level = max(user_level, group.max_amount)

        # Comparaison du niveau de gestionnaire de l'utilisateur auniveau requis
        # return user_level >= required_level
        return maxamountapproval

    def action_request_approval(self):
        # Sélection du gestionnaire avec le moins d'approbations en attente d'assignation (optionnel)
        manager = self.select_manager()
        if not manager:
            return

        # Création d'une activité pour le gestionnaire sélectionné
        self.activity_schedule(
            'mail.activity_data_todo',
            user_id=manager.id,
            note="Demande d'approbation de la commande %s" % self.name,
        )

        # Envoi d'un message à l'utilisateur pour lui signaler que la demande d'approbation a été envoyée au gestionnaire
        self.message_post(
            body="La demande d'approbation de la commande a été envoyée au gestionnaire %s" % manager.name)

        # Renvoi d'une action pour afficher la commande et lui demander l'approbation
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def select_manager(self):
        """
        Sélection du gestionnaire avec le moins d'approbations en attente d'assignation (optionnel).
        """
        # Récupération des gestionnaires ayant un niveau supérieur ou égal au niveau requis
        managers = self.env['res.users'].search([('approved_orders_count', '<', 5)])

        if not managers:
            return

        # Tri des gestionnaires par nombre d'approbations en attente d'assignation
        sorted_managers = sorted(managers, key=lambda x: x.approved_orders_count)

        # Renvoi du gestionnaire avec le moins d'approbations en attente d'assignation
        return sorted_managers[0]

    def activity_schedule(self, summary, **kwargs):
        """
        Création d'une activité.
        """
        self.activity_schedule_with_view(
            'mail.mail_activity_data_warning',
            summary=summary,
            **kwargs
        )

    def activity_schedule_with_view(self, view_id, summary, **kwargs):
        """
        Création d'une activité avec une vue spécifique.
        """
        self.ensure_one()
        ctx = kwargs.pop('context', {})
        ctx['default_res_id'] = self.id
        ctx['default_res_model'] = self._name
        ctx['default_activity_type_id'] = self.env.ref(view_id).id
        ctx['default_summary'] = summary
