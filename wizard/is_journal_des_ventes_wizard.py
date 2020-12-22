# -*- coding: utf-8 -*-

from odoo import api, fields, models
import time
import datetime


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
    def tva(self, journee_service,tax_id=False, service=False):
        cr=self._cr
        sql="""
            select
                sum(tva)
            from (
                select 
                    po.id order_id,
                    pol.id,
                    round(sum(pol.price_unit*pol.qty*(1-pol.discount/100)),2) tva
                from pos_order_line pol inner join pos_order po on pol.order_id=po.id
                                        inner join account_tax_pos_order_line_rel rel on rel.pos_order_line_id=pol.id
                                        inner join account_tax at on at.id=rel.account_tax_id
                where po.is_journee_service='"""+str(journee_service)+"""' """
        if tax_id:
            sql=sql+" and at.id="+str(tax_id)+" "

        if service:
            sql=sql+" and po.is_service='"+service+"' "
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
                    round(sum(pol.price_unit*pol.qty*(1-pol.discount/100)),2) ttc
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
    def ht(self, journee_service,tax_id=False, service=False):
        cr=self._cr
        sql="""
            select
                sum(ht)
            from (
                select 
                    po.id order_id,
                    pol.id,
                    round(sum((1-pol.discount/100)*pol.price_unit*pol.qty/(1+at.amount/100)),2) ht
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
        ht=0
        for row in cr.fetchall():
            if row[0]:
                ht=row[0]
        return ht



    @api.multi
    def transaction(self, journee_service, intitule):
        orders=self.env['pos.order'].search([ ('is_journee_service', '=', journee_service)])
        sessions=[]
        for order in orders:
            if order.session_id not in sessions:
                sessions.append(order.session_id)
        val=0
        for session in sessions:
            for statement in session.statement_ids:
                for line in statement.line_ids:
                    if len(line.pos_statement_id)==0:
                        if line.name==intitule:
                            val=val+line.amount
        return val






    @api.multi
    def journal_des_ventes_action(self, data):
        cr=self._cr
        for obj in self:
            date_debut = datetime.datetime.strptime(obj.date_debut, '%Y-%m-%d').strftime('%Y-%m-%d')
            date_fin   = datetime.datetime.strptime(obj.date_fin  , '%Y-%m-%d').strftime('%Y-%m-%d')


            if obj.date_fin>=obj.date_debut:
                jdv_obj=self.env['is.journal.des.ventes']
                while date_debut<=date_fin:
                    nb_ticket = self.nb_ticket(date_debut)
                    if nb_ticket:
                        jdvs=jdv_obj.search([ ('name', '=', date_debut)])
                        if len(jdvs)==0:
                            vals = {
                                'name':        date_debut,
                            }
                            jdv = jdv_obj.create(vals)
                        else:
                            jdv=jdvs[0]

                        ht             = self.ht(date_debut)
                        ttc            = self.ttc(date_debut)
                        ttc_midi       = self.ttc(date_debut,'midi')
                        ttc_soir       = self.ttc(date_debut,'soir')


                        nb_couvert_total=self.nb_couvert(date_debut)
                        couvert_moyen=0
                        couvert_moyen_ht=0
                        if nb_couvert_total!=0:
                            couvert_moyen    = ttc / nb_couvert_total
                            couvert_moyen_ht = ht / nb_couvert_total


                        nb_couvert_soir = self.nb_couvert(date_debut,'soir')
                        nb_couvert_midi = self.nb_couvert(date_debut,'midi')
                        jour_ouvert=0
                        if nb_couvert_midi:
                            jour_ouvert=jour_ouvert+0.5
                        if nb_couvert_soir:
                            jour_ouvert=jour_ouvert+0.5

                        ht_midi=self.ht(date_debut,False, 'midi')
                        couvert_moyen_midi=0
                        if nb_couvert_midi:
                            couvert_moyen_midi=ht_midi/nb_couvert_midi

                        ht_soir=self.ht(date_debut,False, 'soir')
                        couvert_moyen_soir=0
                        if nb_couvert_soir:
                            couvert_moyen_soir=ht_soir/nb_couvert_soir


                        jdv.jour_ouvert             = jour_ouvert

                        jdv.nb_couvert_midi         = nb_couvert_midi
                        jdv.facturation_55_midi     = self.tva(date_debut,41,'midi')
                        jdv.facturation_10_midi     = self.tva(date_debut,8,'midi')
                        jdv.facturation_20_midi     = self.tva(date_debut,1,'midi')
                        jdv.facturation_ttc_midi    = ttc_midi
                        jdv.facturation_ht_midi     = ht_midi
                        jdv.couvert_moyen_midi      = couvert_moyen_midi

                        jdv.nb_couvert_soir         = nb_couvert_soir
                        jdv.facturation_55_soir     = self.tva(date_debut,41,'soir')
                        jdv.facturation_10_soir     = self.tva(date_debut,8,'soir')
                        jdv.facturation_20_soir     = self.tva(date_debut,1,'soir')
                        jdv.facturation_ttc_soir    = ttc_soir
                        jdv.facturation_ht_soir     = ht_soir
                        jdv.couvert_moyen_soir      = couvert_moyen_soir

                        jdv.facturation_ttc_soir    = ttc_soir

                        jdv.nb_couvert_total        = nb_couvert_total
                        jdv.couvert_moyen           = couvert_moyen
                        jdv.couvert_moyen_ht        = couvert_moyen_ht
                        jdv.reglement_cb            = self.reglement(date_debut,'CB')
                        jdv.reglement_cheque        = self.reglement(date_debut,'CH')
                        jdv.reglement_espece        = self.reglement(date_debut,'ESP')
                        jdv.reglement_differe       = self.reglement(date_debut,'DIFF')
                        jdv.reglement_bon_cadeau    = self.reglement(date_debut,'BC')
                        jdv.reglement_total         = self.reglement(date_debut)
                        jdv.facturation_55          = self.tva(date_debut,41)
                        jdv.facturation_10          = self.tva(date_debut,8)
                        jdv.facturation_20          = self.tva(date_debut,1)
                        jdv.facturation_ht          = ht
                        jdv.facturation_ttc         = ttc
                        jdv.achat_bon_cadeau_cb     = self.reglement(date_debut,'BC2')
                        jdv.achat_bon_cadeau_cheque = self.reglement(date_debut,'BC3')
                        jdv.achat_bon_cadeau_espece = self.reglement(date_debut,'BC1')


                        jdv.remise_banque = -self.transaction(date_debut,'BANQUE')
                        jdv.trop_percu    = self.transaction(date_debut,'POURBOIRE')

#                        #** Recherche du pourboire de la journée ***************
#                        orders=self.env['pos.order'].search([ ('is_journee_service', '=', date_debut)])
#                        sessions=[]
#                        for order in orders:
#                            if order.session_id not in sessions:
#                                sessions.append(order.session_id)
#                        trop_percu=0
#                        for session in sessions:
#                            for statement in session.statement_ids:
#                                for line in statement.line_ids:
#                                    if len(line.pos_statement_id)==0:
#                                        if line.name=='POURBOIRE':
#                                            trop_percu=trop_percu+line.amount
#                        jdv.trop_percu=trop_percu
#                        #*******************************************************


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

