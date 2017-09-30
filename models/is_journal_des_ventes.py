# -*- coding: utf-8 -*-

from odoo import api, fields, models
import time


class IsJournalDesVentes(models.Model):
    _name = 'is.journal.des.ventes'
    _order = 'name desc'

    name                    = fields.Date('Date', required=True)
    nb_couvert_midi         = fields.Integer('Nb couverts midi')
    nb_couvert_soir         = fields.Integer('Nb couverts soir')
    nb_couvert_total        = fields.Integer('Nb couverts total')
    couvert_moyen           = fields.Float('Couvert moyen TTC')
    nb_ticket_midi          = fields.Integer('Nb tickets midi')
    nb_ticket_soir          = fields.Integer('Nb tickets soir')
    nb_ticket               = fields.Integer('Nb tickets')
    reglement_cb            = fields.Float('Règlement CB')
    reglement_cheque        = fields.Float('Règlement chèque')
    reglement_espece        = fields.Float('Règlement espèce')
    reglement_differe       = fields.Float('Règlement différé')
    reglement_bon_cadeau    = fields.Float('Règlement bon cadeau')
    reglement_total         = fields.Float('Règlement Total')
    facturation_10          = fields.Float('Facturation TVA 10%')
    facturation_20          = fields.Float('Facturation TVA 20%')
    facturation_ht          = fields.Float('Facturation HT')
    facturation_ttc         = fields.Float('Facturation TTC')
    facturation_ttc_midi    = fields.Float('Facturation TTC midi')
    facturation_ttc_soir    = fields.Float('Facturation TTC soir')
    ticket_moyen_midi       = fields.Float('Ticket moyen midi TTC')
    ticket_moyen_soir       = fields.Float('Ticket moyen soir TTC')
    ticket_moyen_ttc        = fields.Float('Ticket moyen journée TTC')
    ticket_moyen_ht         = fields.Float('Ticket moyen journée HT')
    montant_caisse          = fields.Float('Montant caisse')
    ecart_caisse            = fields.Float('Ecart caisse')
    remise_banque           = fields.Float('Remise en banque')
    ecart_fact_regl         = fields.Float('Ecart facturation / règlement')
    trop_percu              = fields.Float('Trop perçu (Pourboire)')
    achat_bon_cadeau_cb     = fields.Float('Achat bon cadeau CB')
    achat_bon_cadeau_cheque = fields.Float('Achat bon cadeau chèque')
    achat_bon_cadeau_espece = fields.Float('Achat bon cadeau espèce')
    commentaire             = fields.Text('Commentaire')


