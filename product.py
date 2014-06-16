# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import fields, osv
from openerp.tools.translate import _
from datetime import date
from datetime import datetime
from openerp import netsvc

class product_lote_assign(osv.osv_memory):
    _name = 'product.lote.assign'
    _description = 'Product Lote Assign'

    _columns = {
	'lote_id': fields.many2one('elote.lote','Lote'),
	}

    def product_lote_assign(self, cr, uid, ids, context=None):

	product_ids = context['active_ids']
	if len(product_ids) == 0:
		raise osv.except_osv(_('Error!'), _("You should select at least one product!!!"))
		return {'type': 'ir.actions.act_window_close'}
        res_lote = self.read(cr,uid,ids,['lote_id'])
	if not res_lote[0]['lote_id']:
		raise osv.except_osv(_('Error!'), _("You should select at least one lote!!!"))
		return {'type': 'ir.actions.act_window_close'}

	res_lote_id = res_lote[0]['lote_id'][0]
	lote_obj = self.pool.get('elote.lote').browse(cr,uid,res_lote_id)
	list_product_ids = []
	product_obj_ids = self.pool.get('elote.lote').read(cr,uid,res_lote_id,['product_ids'])
	origin_product_ids = []
	for product_id in product_obj_ids['product_ids']:
		origin_product_ids.append(product_id)
		list_product_ids.append(product_id)
	for product_id in product_ids:
		if product_id not in origin_product_ids:
			list_product_ids.append(product_id)

	vals_product = {
	       'product_ids': [(6, 0, list_product_ids)],
		}
	return_id = self.pool.get('elote.lote').write(cr,uid,res_lote_id,vals_product)

        return {}

product_lote_assign()

# vim:expandtab:smartindent:tabstop=4:softtabstop4:shiftwidth=4:

