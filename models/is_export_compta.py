# -*- coding: utf-8 -*-
from openerp import models,fields,api
from openerp.tools.translate import _
import datetime

#from datetime import datetime, timedelta

from openerp.exceptions import Warning
import codecs


def _date_debut():
    now  = datetime.date.today()
    day=now.day
    date= now - datetime.timedelta(days=day)
    day=date.day-1
    date= date - datetime.timedelta(days=day)
    return date.strftime('%Y-%m-%d')


def _date_fin():
    now  = datetime.date.today()
    day=now.day
    date= now - datetime.timedelta(days=day)
    return date.strftime('%Y-%m-%d')



class is_export_compta(models.Model):
    _name='is.export.compta'
    _order='name desc'

    name               = fields.Char("N°Folio"      , readonly=True)
    date_debut         = fields.Date("Date de début", required=True, default=lambda *a: _date_debut())
    date_fin           = fields.Date("Date de fin"  , required=True, default=lambda *a: _date_fin())
    mail_comptable     = fields.Char("Mail du comptable", required=True)
    ligne_ids          = fields.One2many('is.export.compta.ligne', 'export_compta_id', u'Lignes')


    @api.model
    def create(self, vals):
        data_obj = self.env['ir.model.data']
        sequence_ids = data_obj.search([('name','=','is_export_compta_seq')])
        if sequence_ids:
            sequence_id = data_obj.browse(sequence_ids[0].id).res_id
            vals['name'] = self.env['ir.sequence'].get_id(sequence_id, 'id')
        res = super(is_export_compta, self).create(vals)
        return res


    @api.multi
    def action_envoi_mail(self):
        cr=self._cr
        for obj in self:
            sql="""
                SELECT compte,libelle,sum(debit),sum(credit)
                FROM is_export_compta_ligne
                WHERE date>='"""+str(obj.date_debut)+"""' and date <='"""+str(obj.date_fin)+"""'
                GROUP BY compte, libelle
                ORDER BY compte, libelle
            """
            cr.execute(sql)
            html='<table style="width:50%">\n'
            html+='<tr><th>Compte</th><th>Libelle</th><th>Debit</th><th>Credit</th></tr>\n'
            for row in cr.fetchall():
                html+='<tr>'+'<td>'+str(row[0])+'</td>'+'<td>'+str(row[1])+'</td>'+'<td style="text-align:right">'+"{:10.2f}".format(row[2])+'</td>'+'<td style="text-align:right">'+"{:10.2f}".format(row[3])+'</td>'+'</tr>\n'
            html+='</table>\n'
            body_html=u"""
            <html>
              <head>
                <meta content="text/html; charset=UTF-8" http-equiv="Content-Type">
              </head>
              <body>
                <p>Bonjour, </p>
                <p>Veuillez trouver ci-joint le fichier et ci-dessous les totaux : </p>
            """+html+"""
                <p>Cordialement</p>
              </body>
            </html>
            """
            for obj in self:
                user  = self.env['res.users'].browse(self._uid)
                email = user.email
                nom   = user.name
                if email==False:
                    raise Warning(u"Votre mail n'est pas renseigné !")
                if email:
                    attachment_id = self.env['ir.attachment'].search([
                        ('res_model','=','is.export.compta'),
                        ('res_id'   ,'=',obj.id),
                        ('name'     ,'=','export-compta.txt')
                    ])
                    email_vals = {}


                    cc=email
                    to=obj.mail_comptable

                    subject='Export compta Soram du '+str(obj.date_debut)+' au '+str(obj.date_fin)
                    email_vals.update({
                        'subject'       : subject,
                        'email_to'      : to, 
                        'email_cc'      : cc, 
                        'email_from'    : cc, 
                        'body_html'     : body_html.encode('utf-8'), 
                        'attachment_ids': [(6, 0, [attachment_id.id])] 
                    })
                    email_id=self.env['mail.mail'].create(email_vals)
                    if email_id:
                        self.env['mail.mail'].send(email_id)


    @api.multi
    def action_export_compta(self):
        cr=self._cr
        for obj in self:
            obj.ligne_ids.unlink()
            sql="""
                SELECT
                    name,
                    reglement_cb,
                    reglement_cheque,
                    reglement_espece,
                    reglement_differe,
                    reglement_bon_cadeau,
                    achat_bon_cadeau_espece,
                    achat_bon_cadeau_cheque,
                    achat_bon_cadeau_cb,
                    facturation_10,
                    facturation_20,
                    trop_percu,
                    facturation_55
                FROM is_journal_des_ventes
                WHERE name>='"""+str(obj.date_debut)+"""' and name <='"""+str(obj.date_fin)+"""'
                ORDER BY name
            """
            cr.execute(sql)
            for row in cr.fetchall():


                credit=0
                debit=0


                date=row[0]
                if row[1]:
                    compte  = '51110000'
                    libelle = 'Reglement CB'
                    sens    = 'D'
                    montant = row[1]
                    debit=debit+montant
                    self.c(obj.id,date,compte,libelle,sens,montant)

                if row[2]:
                    compte  = '51100000'
                    libelle = 'Reglement Cheque'
                    sens    = 'D'
                    montant = row[2]
                    debit=debit+montant
                    self.c(obj.id,date,compte,libelle,sens,montant)

                if row[3]:
                    compte  = '53000000'
                    libelle = 'Reglement Espece'
                    sens    = 'D'
                    montant = row[3]
                    debit=debit+montant
                    self.c(obj.id,date,compte,libelle,sens,montant)

                if row[4]:
                    compte  = 'CDIVERS'
                    libelle = 'Reglement Differe'
                    sens    = 'D'
                    montant = row[4]
                    debit=debit+montant
                    self.c(obj.id,date,compte,libelle,sens,montant)

                if row[5]:
                    compte  = '41910000'
                    libelle = 'Reglement Bon Cadeaux'
                    sens    = 'D'
                    montant = row[5]
                    debit=debit+montant
                    self.c(obj.id,date,compte,libelle,sens,montant)

                if row[6]:
                    montant = row[6]
                    libelle = 'Vente Bon Cadeaux Espece'
                    self.c(obj.id,date,'41910000',libelle,'C',montant)
                    self.c(obj.id,date,'53000000',libelle,'D',montant)

                if row[7]:
                    montant = row[7]
                    compte  = '41910000'
                    libelle = 'Vente Bon Cadeaux Cheque'
                    self.c(obj.id,date,'41910000',libelle,'C',montant)
                    self.c(obj.id,date,'51100000',libelle,'D',montant)

                if row[8]:
                    montant = row[8]
                    compte  = '41910000'
                    libelle = 'Vente Bon Cadeaux CB'
                    self.c(obj.id,date,'41910000',libelle,'C',montant)
                    self.c(obj.id,date,'51110000',libelle,'D',montant)


                if row[9]:
                    compte  = '70750000'
                    libelle = 'Facturation TVA 10%'
                    sens    = 'C'
                    montant = row[9]
                    credit=credit+montant
                    self.c(obj.id,date,compte,libelle,sens,montant)

                if row[10]:
                    compte  = '70716000'
                    libelle = 'Facturation TVA 20%'
                    sens    = 'C'
                    montant = row[10]
                    credit=credit+montant
                    self.c(obj.id,date,compte,libelle,sens,montant)

                if row[11]:
                    compte  = ''
                    libelle = 'Ecart facture pour service'
                    montant = row[11]
                    self.c(obj.id,date,'46710000',libelle,'C',montant)
                    self.c(obj.id,date,'53000000',libelle,'D',montant)

                if row[12]:
                    compte  = '70721000'
                    libelle = 'Facturation TVA 5.5%'
                    sens    = 'C'
                    montant = row[12]
                    credit=credit+montant
                    self.c(obj.id,date,compte,libelle,sens,montant)

                ecart=round(credit-debit,2)
                if ecart:
                    montant=-ecart
                    compte  = '46710000'
                    libelle = 'Ecart debit credit'
                    if montant<0:
                        montant=-montant
                        sens='D'
                        debit=debit+montant
                    else:
                        sens='C'
                        credit=credit+montant

                    self.c(obj.id,date,compte,libelle,sens,montant)
            self.generer_fichier()

    def c(self,export_compta_id,date,compte,libelle,sens,montant):
        debit  = 0
        credit = 0
        if sens=='D':
            debit=montant
        else:
            credit=montant

        vals={
            'export_compta_id'  : export_compta_id,
            'date'              : date,
            'compte'            : compte,
            'libelle'           : libelle,
            'debit'             : debit,
            'credit'            : credit,
        }
        self.env['is.export.compta.ligne'].create(vals)



    def generer_fichier(self):
        for obj in self:
            model='is.export.compta'
            attachments = self.env['ir.attachment'].search([('res_model','=',model),('res_id','=',obj.id)])
            attachments.unlink()
            name='export-compta.txt'
            dest     = '/tmp/'+name
            f = codecs.open(dest,'wb',encoding='utf-8')


            for row in obj.ligne_ids:




                compte=str(row.compte)

                debit=row.debit
                credit=row.debit
                if row.credit>0.0:
                    montant=row.credit  
                    sens='C'
                else:
                    montant=row.debit  
                    sens='D'
                montant=(u'000000000000'+'%0.2f' % montant)[-12:]

                date=row.date
                date=datetime.datetime.strptime(date, '%Y-%m-%d')
                date=date.strftime('%d/%m/%Y')
                libelle=row.libelle or u'??'
                libelle=(libelle+u'                    ')[0:30]


#                Chaque ligne doit être comme tel :
#                JOURNAL – DATE – COMPTE – LIBELLE – MONTANT (au débit ou au crédit en fonction du compte).
#                VE  01/06/2018 51110000  REMISE CB 01/06   1152,10

                f.write('VE')
                f.write(date)
                f.write((compte+u'        ')[0:8])
                f.write(libelle)
                f.write(sens)
                f.write(montant)
                f.write('\r\n')
            f.close()
            r = open(dest,'rb').read().encode('base64')
            vals = {
                'name':        name,
                'datas_fname': name,
                'type':        'binary',
                'res_model':   model,
                'res_id':      obj.id,
                'datas':       r,
            }
            id = self.env['ir.attachment'].create(vals)


class is_export_compta_ligne(models.Model):
    _name = 'is.export.compta.ligne'
    _description = u"Lignes d'export en compta"
    _order='date'

    export_compta_id = fields.Many2one('is.export.compta', 'Export Compta', required=True, ondelete='cascade')
    date     = fields.Date("Date")
    compte   = fields.Char("N°Compte")
    libelle  = fields.Char("Libellé")
    debit    = fields.Float("Débit")
    credit   = fields.Float("Crédit")



