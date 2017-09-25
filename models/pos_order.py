# -*- coding: utf-8 -*-

from odoo import api, fields, models
import time
import datetime
import pytz

class PosOrder(models.Model):
    _inherit = "pos.order"

    is_nb_couverts     = fields.Integer(string='Nombre de couverts')
    is_couvert_moyen   = fields.Float(string='Couvert moyen')
    is_serveur_id      = fields.Many2one('product.product', 'Serveur')
    is_origine_id      = fields.Many2one('product.product', 'Origine du client')
    is_reservation_id  = fields.Many2one('product.product', 'Réservation')
    is_journee_service = fields.Date(string='Journée du service')
    is_service         = fields.Selection([('midi', 'Midi'),('soir', 'Soir')], "Service")

    @api.model
    def create(self, vals):
        obj = super(PosOrder, self).create(vals)
        is_serveur_id     = False
        is_origine_id     = False
        is_reservation_id = False
        nb=0
        for line in obj.lines:
            categ=line.product_id.pos_categ_id.name
            if categ=='Provenance du client':
                is_origine_id=line.product_id.id
            if categ=='Serveur':
                is_serveur_id=line.product_id.id
            if categ==u'Réservation':
                is_reservation_id=line.product_id.id
            if categ=='Menu':
                nb=nb+line.qty
        obj.is_nb_couverts    = nb
        obj.is_serveur_id     = is_serveur_id
        obj.is_origine_id     = is_origine_id
        obj.is_reservation_id = is_reservation_id

        #** Journée du service *************************************************
        date = datetime.datetime.now(pytz.timezone('Europe/Paris'))
        print date.strftime('%Y-%m-%d'), date.strftime('%H:%M')
        if date.strftime('%H')<'09':
            date=date+datetime.timedelta(days=-1) # Date -1 jour
        obj.is_journee_service=date.strftime('%Y-%m-%d') 
        #***********************************************************************

        #** Service ************************************************************
        service="midi"
        date = datetime.datetime.now(pytz.timezone('Europe/Paris'))
        if date.strftime('%H')<'09' or date.strftime('%H')>'18' :
            service="soir"
        obj.is_service=service
        #***********************************************************************

        if nb==0:
            nb=1
        obj.is_couvert_moyen=obj.amount_total/nb


        return obj


class PosOrderLine(models.Model):
    _inherit = "pos.order.line"

    note = fields.Text(string='Note')

