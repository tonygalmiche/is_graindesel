# -*- coding: utf-8 -*-

from odoo import api, fields, models
import time


class IsJournalDesVentes(models.Model):
    _name = 'is.journal.des.ventes'
    _order = 'name desc'

    name             = fields.Date('Date', required=True)
    nb_couvert_midi  = fields.Integer('Nb couverts midi')
    nb_couvert_soir  = fields.Integer('Nb couverts soir')
    nb_couvert_total = fields.Integer('Nb couverts total')
    couvert_moyen    = fields.Float('Couvert moyen TTC')
    nb_ticket        = fields.Integer('Nb tickets')
    reglement_cb     = fields.Float('Règlement CB')
    reglement_cheque = fields.Float('Règlement chèque')
    reglement_espece = fields.Float('Règlement espèce')
    reglement_total  = fields.Float('Règlement Total')
    facturation_10   = fields.Float('Facturation TVA 10%')
    facturation_20   = fields.Float('Facturation TVA 20%')
    facturation_ttc  = fields.Float('Facturation TTC')
    facturation_ht   = fields.Float('Facturation HT')
    ticket_moyen_ttc = fields.Float('Ticket moyen TTC')
    ticket_moyen_ht  = fields.Float('Ticket moyen HT')
    ecart_fact_regl  = fields.Float('Ecart facturation / règlement')

