from datetime import timedelta

from odoo import api, models, fields

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    approved_orders_count = fields.Integer(string="Nombre de commandes approuvées", compute="_compute_approved_orders_count")
    training_date = fields.Date(string="Date de la formation", required=True)

    def _compute_approved_orders_count(self):
        for order in self:
            order.approved_orders_count = self.env['sale.order'].search_count([
                ('user_id', '=', self.env.user.id),
                ('state', '=', 'sale'),
            ])

    @api.model
    def open_training_date_wizard(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Date de formation',
            'res_model': 'sale.order',
            'res_id': self.id,
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': self.env.ref('sale.view_form_sale_order_wizard').id,
            'target': 'new',
        }

    def action_confirm(self):
        # Récupération du partenaire associé à la commande en cours
        partner = self.partner_id
        max_amount = self.user_has_required_level()
        order_line = self.order_line[0]

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
                event = self.env['calendar.event'].create({
                    'name': 'Formation Odoo',
                    'start': order.training_date,
                    'stop': order.training_date + timedelta(hours=8),
                    'allday': True,
                    'partner_ids': [(4, partner.id)],
                })

            self.env.user.approved_orders_count += 1

            self.message_post(body="La commande a été approuvée par %s" % self.env.user.name)

            # Confirmation de la commande
            return super(SaleOrder, self).action_confirm()

        else:
            self.message_post(
                body="La commande nécessite une approbation de la part d'un gestionnaire de niveau supérieur.")

            # Renvoi d'une action pour afficher la commande et lui demander l'approbation
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'sale.order',
                'res_id': self.id,
                'view_mode': 'form',
                'target': 'current',
            }

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

        # Comparaison du niveau de gestionnaire de l'utilisateur au niveau requis
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
        Sélectionne le gestionnaire avec le moins d'approbations en attente d'assignation.
        """
        # Récupération de tous les gestionnaires de l'entreprise
        managers = self.env['res.users'].search([('groups_id', 'in', self.env.ref('base.group_user').id)])
        if not managers:
            return

        # Initialisation du gestionnaire sélectionné à la première valeur de la liste de gestionnaires
        selected_manager = managers[0]

        # Recherche du gestionnaire avec le moins d'approbations en attente d'assignation
        for manager in managers:
            # Récupération des activités en attente d'assignation du gestionnaire
            pending_approvals = self.env['mail.activity'].search_count([
                ('user_id', '=', manager.id),
                ('state', '=', 'to_do'),
            ])
            # Comparaison du nombre d'approbations en attente du gestionnaire courant au nombre d'approbations en attente du gestionnaire sélectionné
            # Récupération du nombre d'approbations en attente du gestionnaire sélectionné
            selected_manager_pending_approvals = self.env['mail.activity'].search_count([
                ('user_id', '=', selected_manager.id),
                ('state', '=', 'to_do'),
            ])
            # Si le nombre d'approbations en attente du gestionnaire courant est inférieur au nombre d'approbations en attente du gestionnaire sélectionné, le gestionnaire courant devient le gestionnaire sélectionné
            if pending_approvals < selected_manager_pending_approvals:
                selected_manager = manager

        # Renvoi du gestionnaire sélectionné
        return selected_manager


