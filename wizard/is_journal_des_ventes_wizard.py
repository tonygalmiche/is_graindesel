# -*- coding: utf-8 -*-

from odoo import api, fields, models
import time
import datetime


class IsJournalDesVentesWizard(models.TransientModel):
    _name = 'is.journal.des.ventes.wizard'

    date_debut = fields.Date('Date de début', required=True,  default=lambda *a: time.strftime('%Y-%m-%d'))
    date_fin   = fields.Date('Date de fin'  , required=True,  default=lambda *a: time.strftime('%Y-%m-%d'))


    @api.multi
    def journal_des_ventes_action(self, data):
        for obj in self:


            date_debut = datetime.datetime.strptime(obj.date_debut, '%Y-%m-%d').strftime('%Y-%m-%d')
            date_fin   = datetime.datetime.strptime(obj.date_fin  , '%Y-%m-%d').strftime('%Y-%m-%d')

            print obj.date_debut, obj.date_fin, type(obj.date_fin), date_debut


            if obj.date_fin>=obj.date_debut:
                jdv_obj=self.env['is.journal.des.ventes']
                while date_debut<=date_fin:
                    jdv=jdv_obj.search([ ('name', '=', date_debut)])
                    print date_debut, jdv
                    jdv.unlink()
                    vals = {
                        'name':        date_debut,
                    }
                    jdv = jdv_obj.create(vals)
                    print jdv, vals




                    date_debut = datetime.datetime.strptime(date_debut, '%Y-%m-%d')
                    date_debut = date_debut + datetime.timedelta(days=1)
                    date_debut = date_debut.strftime('%Y-%m-%d')


        return {
            'name': u'Journal des Ventes ',
            'view_mode': 'tree,form',
            'view_type': 'form',
            'res_model': 'is.journal.des.ventes',
            'domain': [],
            'context':{},
            'type': 'ir.actions.act_window',
        }






#  now  = datetime.date.today()               # Date du jour
#  date = now + datetime.timedelta(days=-1)   # Date -1 jour
#  return date.strftime('%Y-%m-%d')         
