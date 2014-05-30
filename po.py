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


class purchase_order(osv.osv):
	_name = 'purchase.order'
	_inherit = 'purchase.order'

	_columns = {
		'exception_ids': fields.one2many('purchase.order.exception','order_id','Excepciones'),
		}

purchase_order()

class purchase_order_exceptions(osv.osv):
	_name = 'purchase.order.exception'
	_description = 'Exceptions to POs'

	_columns = {
		'order_id': fields.many2one('purchase.order','Pedido'),
		'product_id': fields.many2one('product.product','Producto'),
		'reason': fields.selection((('1','No llega al mínimo de producción'),('2','Otros motivos')),'Razón de rechazo'),
		'qty': fields.integer('Quantity'),
		}

purchase_order_exceptions()

class po_merge(osv.osv_memory):
    _name = 'po.merge'
    _description = 'PO Merge Wizard'

    def po_merge(self, cr, uid, ids, context=None):

	order_ids = context['active_ids']
	if len(order_ids) == 0:
		raise osv.except_osv(_('Error!'), _("You should select at least one purchase order!!!"))
		return {'type': 'ir.actions.act_window_close'}

	list_orders = []
	for order in self.pool.get('purchase.order').browse(cr,uid,order_ids):
		if order.state in ['confirmed','approved']:
			add_item = True
			index = 0
			for list_order in list_orders:
				if list_order['partner_id'] == order.partner_id.id:
					list_orders[index]['order_ids'].append(order.id)
					add_item = False
				index += 1	
			if add_item:
				vals_order = {
					'partner_id': order.partner_id.id,
					'order_ids': [order.id],
					'name': order.partner_id.name,
					'stock_supplier': order.partner_id.property_stock_supplier.id,
					}
				list_orders.append(vals_order)

	for list_order in list_orders:
		vals_purchase_order = {
			'name': 'AUT PO '+list_order['name'] + str(datetime.now()),
			'partner_id': list_order['partner_id'],
			'invoice_method': 'order',
			'location_id': list_order['stock_supplier'],
			'pricelist_id': 1
			}
		

		return_id = self.pool.get('purchase.order').create(cr,uid,vals_purchase_order)
		order_id = return_id
		list_lines = []
		list_products = []
		for order in list_order['order_ids']:
			order_obj = self.pool.get('purchase.order').browse(cr,uid,order)
			line_ids = self.pool.get('purchase.order.line').search(cr,uid,[('order_id','=',order)])
			for line in self.pool.get('purchase.order.line').browse(cr,uid,line_ids):
				add_item = True
				index = 0
				for list_product in list_products:
					if list_product['product_id'] == line.product_id.id:
						list_products[index]['qty'] += line.product_qty
						add_item = False
					index += 1	
				if add_item:
					vals_product = {
						'product_id': line.product_id.id,
						'qty': line.product_qty,
						'price_unit': line.product_id.list_price,
						'product_uom': line.product_id.uom_id.id,
						'name': line.product_id.name,
						'date_planned': line.date_planned,
						}
					list_products.append(vals_product)
		for list_product in list_products:
			product = self.pool.get('product.product').browse(cr,uid,list_product['product_id'])
			# import pdb;pdb.set_trace()
			product_supplier_id = self.pool.get('product.supplierinfo').search(cr,uid,[('product_tmpl_id','=',product.product_tmpl_id.id),\
											('name','=',list_order['partner_id'])])
			insert_product = True
			# import pdb;pdb.set_trace()
			if product_supplier_id:
				product_supplier = self.pool.get('product.supplierinfo').browse(cr,uid,product_supplier_id)[0]
				if product_supplier.min_qty > list_product['qty']:
					insert_product = False
			if insert_product:	
				vals_order_line = {
					'order_id': order_id,
					'product_id': list_product['product_id'],
					'name': list_product['name'],
					'product_uom': list_product['product_uom'],
					'product_qty': list_product['qty'],
					'price_unit': list_product['price_unit'],
					'date_planned': list_product['date_planned'],
					}
				return_id = self.pool.get('purchase.order.line').create(cr,uid,vals_order_line)
			else:
				vals_purchase_order_exception = {
					'product_id': list_product['product_id'],
					'order_id': order_id,
					'reason': '1',
					'qty': list_product['qty'],
					}
				exception_obj = self.pool.get('purchase.order.exception')
				return_id = exception_obj.create(cr,uid,vals_purchase_order_exception)
				

        return {}

po_merge()

# vim:expandtab:smartindent:tabstop=4:softtabstop4:shiftwidth=4:

