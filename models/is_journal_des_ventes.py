# -*- coding: utf-8 -*-

from odoo import api, fields, models
import time


class IsJournalDesVentes(models.Model):
    _name = 'is.journal.des.ventes'
    _order = 'name desc'

    name                    = fields.Date('Date', required=True)
    jour_ouvert             = fields.Float('Jour ouvert', digits=(12,1))

    nb_couvert_midi         = fields.Integer('Nb couverts midi')
    facturation_10_midi     = fields.Float('Facturation TVA 10% midi')
    facturation_20_midi     = fields.Float('Facturation TVA 20% midi')
    facturation_ttc_midi    = fields.Float('Facturation TTC midi')
    facturation_ht_midi     = fields.Float('Facturation HT midi')
    couvert_moyen_midi      = fields.Float('Couvert moyen HT midi')

    nb_couvert_soir         = fields.Integer('Nb couverts soir')
    facturation_10_soir     = fields.Float('Facturation TVA 10% soir')
    facturation_20_soir     = fields.Float('Facturation TVA 20% soir')
    facturation_ttc_soir    = fields.Float('Facturation TTC soir')
    facturation_ht_soir     = fields.Float('Facturation HT soir')
    couvert_moyen_soir      = fields.Float('Couvert moyen HT soir')

    nb_couvert_total        = fields.Integer('Nb couverts total')

    reglement_cb            = fields.Float('Règlement CB')
    reglement_cheque        = fields.Float('Règlement chèque')
    reglement_espece        = fields.Float('Règlement espèce')
    reglement_differe       = fields.Float('Règlement différé')
    reglement_bon_cadeau    = fields.Float('Règlement bon cadeau')
    reglement_total         = fields.Float('Règlement Total')

    achat_bon_cadeau_cb     = fields.Float('Achat bon cadeau CB')
    achat_bon_cadeau_cheque = fields.Float('Achat bon cadeau chèque')
    achat_bon_cadeau_espece = fields.Float('Achat bon cadeau espèce')

    facturation_10          = fields.Float('Facturation TVA 10%')
    facturation_20          = fields.Float('Facturation TVA 20%')
    facturation_ttc         = fields.Float('Facturation TTC')
    facturation_ht          = fields.Float('Facturation HT')

    couvert_moyen           = fields.Float('Couvert moyen TTC')
    couvert_moyen_ht        = fields.Float('Couvert moyen HT')

    montant_caisse          = fields.Float('Montant caisse')
    ecart_caisse            = fields.Float('Ecart caisse')
    remise_banque           = fields.Float('Remise en banque')
    ecart_fact_regl         = fields.Float('Ecart facturation / règlement')
    trop_percu              = fields.Float('Trop perçu (Pourboire)')
    commentaire             = fields.Text('Commentaire')



    @api.multi
    def action_point_de_vente(self):
        for obj in self:
            return {
                'name': u'Point de vente',
                'view_type': 'form',
                'view_mode': 'form,tree',
                'res_model': 'pos.config',
                'res_id': 1,
                'type': 'ir.actions.act_window',
            }


    @api.multi
    def action_sessions(self):
        for obj in self:
            orders=self.env['pos.order'].search([ ('is_journee_service', '=', obj.name)])
            sessions=[]
            for order in orders:
                if order.session_id.id not in sessions:
                    sessions.append(order.session_id.id)
            return {
                'name': u'Sessions',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'pos.session',
                'type': 'ir.actions.act_window',
                'domain': [
                    ('id','in',sessions),
                ],
            }


    @api.multi
    def action_commandes(self):
        for obj in self:
            orders=self.env['pos.order'].search([ ('is_journee_service', '=', obj.name)])
            res=[]
            for order in orders:
                res.append(order.id)
            return {
                'name': u'Sessions',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'pos.order',
                'type': 'ir.actions.act_window',
                'domain': [
                    ('id','in',res),
                ],

            }


    @api.multi
    def action_paiements(self):
        for obj in self:
            orders=self.env['pos.order'].search([ ('is_journee_service', '=', obj.name)])
            res=[]
            for order in orders:
                #res.append(order.session_id.statement_ids)
                for statement in order.session_id.statement_ids:
                    if statement.id not in res:
                        res.append(statement.id)
            return {
                'name': u'Sessions',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'account.bank.statement',
                'type': 'ir.actions.act_window',
                'domain': [
                    ('id','in',res),
                ],

            }


    @api.multi
    def action_ecriture_comptables(self):
        for obj in self:
            orders=self.env['pos.order'].search([ ('is_journee_service', '=', obj.name)])
            moves=[]
            statements=[]
            for order in orders:
                if order.account_move.id not in moves:
                    moves.append(order.account_move.id)
                    for statement in order.session_id.statement_ids:
                        if statement.id not in statements:
                            statements.append(statement.id)
            return {
                'name': u'Sessions',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'account.move.line',
                'type': 'ir.actions.act_window',
                'domain': [
                    '|',('move_id','in',moves),('statement_id','in',statements),
                ],

            }

