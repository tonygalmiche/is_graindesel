# -*- coding: utf-8 -*-

from odoo import api, fields, models
import time
import datetime


## TODO : Recherche des montant par type de TVA

# select * from pos_order_line;
# select * from account_tax_pos_order_line_rel ;
# select name,description,amount from account_tax where id=8;
#  name   | description | amount  
#---------+-------------+---------
# TVA 10% | 10.0-TTC    | 10.0000




class IsJournalDesVentesWizard(models.TransientModel):
    _name = 'is.journal.des.ventes.wizard'

    date_debut = fields.Date('Date de début', required=True,  default=lambda *a: time.strftime('%Y-%m-%d'))
    date_fin   = fields.Date('Date de fin'  , required=True,  default=lambda *a: time.strftime('%Y-%m-%d'))


    @api.multi
    def nb_couvert(self, journee_service, service=False):
        cr=self._cr
        sql="""
            select sum(po.is_nb_couverts)
            from pos_order po
            where po.is_journee_service='"""+str(journee_service)+"""'
        """
        if service:
            sql=sql+" and po.is_service='"+service+"' "
        cr.execute(sql)
        nb_couvert=0
        for row in cr.fetchall():
            if row[0]:
                nb_couvert=row[0]
        return nb_couvert


    @api.multi
    def nb_ticket(self, journee_service, service=False):
        cr=self._cr
        sql="""
            select count(po.id)
            from pos_order po
            where po.is_journee_service='"""+str(journee_service)+"""'
        """
        if service:
            sql=sql+" and po.is_service='"+service+"' "
        cr.execute(sql)
        nb_ticket=0
        for row in cr.fetchall():
            if row[0]:
                nb_ticket=row[0]
        return nb_ticket


    @api.multi
    def reglement(self, journee_service,code_journal=False):
        cr=self._cr
        sql="""
            select sum(absl.amount)
            from account_bank_statement_line absl inner join account_journal aj on absl.journal_id=aj.id
                                                  inner join  pos_order po on absl.pos_statement_id=po.id
            where 
                po.is_journee_service='"""+str(journee_service)+"""'  
        """
        if code_journal:
            sql=sql+" and aj.code='"+code_journal+"' "
        else:
            sql=sql+" and aj.code not in ('BC1','BC2','BC3') "
        cr.execute(sql)
        reglement=0
        for row in cr.fetchall():
            if row[0]:
                reglement=row[0]
        return reglement


    @api.multi
    def tva(self, journee_service,tax_id=False):
        cr=self._cr
        sql="""
            select
                sum(tva)
            from (
                select 
                    po.id order_id,
                    pol.id,
                    round(sum(pol.price_unit*pol.qty),2) tva
                from pos_order_line pol inner join pos_order po on pol.order_id=po.id
                                        inner join account_tax_pos_order_line_rel rel on rel.pos_order_line_id=pol.id
                                        inner join account_tax at on at.id=rel.account_tax_id
                where po.is_journee_service='"""+str(journee_service)+"""' """

        #round(sum(pol.price_unit*pol.qty-pol.price_unit*pol.qty/(1+at.amount/100)),2) tva


        if tax_id:
            sql=sql+" and at.id="+str(tax_id)+" "
        sql=sql+"""
                group by po.id,pol.id
            ) pol
        """
        cr.execute(sql)
        tva=0
        for row in cr.fetchall():
            if row[0]:
                tva=row[0]
        return tva


    @api.multi
    def ttc(self, journee_service, service=False):
        cr=self._cr
        sql="""
            select
                sum(ttc)
            from (
                select 
                    po.id order_id,
                    pol.id,
                    round(sum(pol.price_unit*pol.qty),2) ttc
                from pos_order_line pol inner join pos_order po on pol.order_id=po.id
                                        inner join account_tax_pos_order_line_rel rel on rel.pos_order_line_id=pol.id
                                        inner join account_tax at on at.id=rel.account_tax_id
                where po.is_journee_service='"""+str(journee_service)+"""' """
        if service:
            sql=sql+" and po.is_service='"+service+"' "
        sql=sql+"""
                group by po.id,pol.id
            ) pol
        """
        cr.execute(sql)
        ttc=0
        for row in cr.fetchall():
            if row[0]:
                ttc=row[0]
        return ttc


    @api.multi
    def ht(self, journee_service,tax_id=False):
        cr=self._cr
        sql="""
            select
                sum(ht)
            from (
                select 
                    po.id order_id,
                    pol.id,
                    round(sum(pol.price_unit*pol.qty/(1+at.amount/100)),2) ht
                from pos_order_line pol inner join pos_order po on pol.order_id=po.id
                                        inner join account_tax_pos_order_line_rel rel on rel.pos_order_line_id=pol.id
                                        inner join account_tax at on at.id=rel.account_tax_id
                where po.is_journee_service='"""+str(journee_service)+"""'
                group by po.id,pol.id
            ) pol
        """
        cr.execute(sql)
        ht=0
        for row in cr.fetchall():
            if row[0]:
                ht=row[0]
        return ht


    @api.multi
    def journal_des_ventes_action(self, data):
        cr=self._cr
        for obj in self:
            date_debut = datetime.datetime.strptime(obj.date_debut, '%Y-%m-%d').strftime('%Y-%m-%d')
            date_fin   = datetime.datetime.strptime(obj.date_fin  , '%Y-%m-%d').strftime('%Y-%m-%d')
            if obj.date_fin>=obj.date_debut:
                jdv_obj=self.env['is.journal.des.ventes']
                while date_debut<=date_fin:
                    jdvs=jdv_obj.search([ ('name', '=', date_debut)])
                    if len(jdvs)==0:
                        vals = {
                            'name':        date_debut,
                        }
                        jdv = jdv_obj.create(vals)
                    else:
                        jdv=jdvs[0]

                    nb_ticket      = self.nb_ticket(date_debut)
                    nb_ticket_midi = self.nb_ticket(date_debut,'midi')
                    nb_ticket_soir = self.nb_ticket(date_debut,'soir')
                    ht             = self.ht(date_debut)
                    ttc            = self.ttc(date_debut)
                    ttc_midi       = self.ttc(date_debut,'midi')
                    ttc_soir       = self.ttc(date_debut,'soir')

                    ticket_moyen_midi=0
                    if nb_ticket_midi!=0:
                        ticket_moyen_midi=ttc_midi/nb_ticket_midi
                    ticket_moyen_soir=0
                    if nb_ticket_soir!=0:
                        ticket_moyen_soir=ttc_soir/nb_ticket_soir
                    ticket_moyen_ttc=0
                    if nb_ticket!=0:
                        ticket_moyen_ttc=ttc/nb_ticket
                    ticket_moyen_ht=0
                    if nb_ticket!=0:
                        ticket_moyen_ht=ht/nb_ticket

                    nb_couvert_total=self.nb_couvert(date_debut)
                    couvert_moyen=0
                    couvert_moyen_ht=0
                    if nb_couvert_total!=0:
                        couvert_moyen    = ttc / nb_couvert_total
                        couvert_moyen_ht = ht / nb_couvert_total


                    jdv.nb_couvert_midi         = self.nb_couvert(date_debut,'midi')
                    jdv.nb_couvert_soir         = self.nb_couvert(date_debut,'soir')
                    jdv.nb_couvert_total        = nb_couvert_total
                    jdv.couvert_moyen           = couvert_moyen
                    jdv.couvert_moyen_ht        = couvert_moyen_ht
                    jdv.nb_ticket_midi          = nb_ticket_midi
                    jdv.nb_ticket_soir          = nb_ticket_soir
                    jdv.nb_ticket               = nb_ticket
                    jdv.reglement_cb            = self.reglement(date_debut,'CB')
                    jdv.reglement_cheque        = self.reglement(date_debut,'CH')
                    jdv.reglement_espece        = self.reglement(date_debut,'ESP')
                    jdv.reglement_differe       = self.reglement(date_debut,'DIFF')
                    jdv.reglement_bon_cadeau    = self.reglement(date_debut,'BC')
                    jdv.reglement_total         = self.reglement(date_debut)
                    jdv.facturation_10          = self.tva(date_debut,8)
                    jdv.facturation_20          = self.tva(date_debut,1)
                    jdv.facturation_ht          = ht
                    jdv.facturation_ttc         = ttc
                    jdv.facturation_ttc_midi    = ttc_midi
                    jdv.facturation_ttc_soir    = ttc_soir
                    jdv.ticket_moyen_midi       = ticket_moyen_midi
                    jdv.ticket_moyen_soir       = ticket_moyen_soir
                    jdv.ticket_moyen_ttc        = ticket_moyen_ttc
                    jdv.ticket_moyen_ht         = ticket_moyen_ht
                    #jdv.montant_caisse          = 10
                    #jdv.ecart_caisse            = 10
                    #jdv.remise_banque           = 10
                    #jdv.ecart_fact_regl         = 10
                    #jdv.trop_percu              = 10
                    jdv.achat_bon_cadeau_cb     = self.reglement(date_debut,'BC2')
                    jdv.achat_bon_cadeau_cheque = self.reglement(date_debut,'BC3')
                    jdv.achat_bon_cadeau_espece = self.reglement(date_debut,'BC1')

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
