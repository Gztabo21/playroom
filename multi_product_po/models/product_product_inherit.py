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


class ProductProductInherit(models.Model):
	_inherit = 'product.product'

	product_qty_aux = fields.Float(string="Cantidad", default=0)
		
ProductProductInherit()
