# -*- coding: utf-8 -*-

from odoo import api, fields, models


class PosSession(models.Model):
    _inherit = "pos.session"


    @api.multi
    def action_transactions(self):
        for obj in self:
            dummy, view_id = self.env['ir.model.data'].get_object_reference('is_graindesel', 'is_account_bank_statement_line_tree_view')
            lines=[]
            for row in obj.statement_ids:
                lines.append(row.id)
            return {
                'name': u'Transactions',
                'view_type': 'form',
                'view_mode': 'tree',
                'res_model': 'account.bank.statement.line',
                'type': 'ir.actions.act_window',
                'view_id': view_id,
                'domain': [
                    ('statement_id','in',lines),
                    ('pos_statement_id','=',False),
                ],
            }

