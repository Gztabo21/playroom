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

from odoo import fields, models, _
from odoo.addons import decimal_precision as dp


class SaleOrderTax(models.Model):
    _name = "sale.order.tax"
    _order = "sequence"

    order_id = fields.Many2one("sale.order", string="Sale Order", ondelete="cascade")
    name = fields.Char(string=u"Descripción Impuesto", required=True)
    base = fields.Float(
        string="Base", digits=dp.get_precision("Product Unit of Measure")
    )
    amount = fields.Float(
        string="Amount", digits=dp.get_precision("Product Unit of Measure")
    )
    sequence = fields.Integer(
        string="Sequence",
        help="Gives the sequence order when displaying a list of order tax.",
    )
    account_id = fields.Many2one(
        "account.account",
        string="Cuenta",
        required=False,
        domain=[("deprecated", "=", False)],
    )
