#   coding: utf-8
##############################################################################
#
#   Copyright (C) 2021 Odoo Inc
#   Autor: Brayhan Andres Jaramillo Castaño
#   Correo: brayhanjaramillo@hotmail.com
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.     
#
##############################################################################
import time
from odoo import models, api, fields, _
from odoo.exceptions import UserError


class SaleOrderMultiProduct(models.TransientModel):
	_name = 'sale.order.multi.product'
	_description = 'Multiple producto en Orden de Venta'

	product_ids = fields.Many2many('product.product', 'sale_order_multi_product_rel', 'wizard_id', "product_id", string="Productos", domain="[('sale_ok', '=', True), '|', ('company_id', '=', False)]")

	def return_data_product(self):
		data = []
		if self.product_ids:
			for product in self.product_ids:
				vals = {
					'product_id': product.id,
					'name': product.display_name,
					'product_uom_qty': product.product_qty_aux,
					'product_uom': product.uom_id.id,

				}
				data.append((0, 0, vals))
		return data

	def load_order_line(self):
		context = self.env.context
		if 'sale_id' in context:
			sale_id = self.env['sale.order'].browse([context['sale_id']])
			if sale_id:
				data = self.return_data_product()
				print(data)
				sale_id.sudo().write({'order_line': data})
				product_ids = self.product_ids.ids
				for product in sale_id.order_line:
					if product.id in product_ids:
						product.product_id_change()

SaleOrderMultiProduct()
