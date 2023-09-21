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
from odoo import models, _


class SaleAdvancePaymentInvInherit(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    def _create_invoice(self, order, so_line, amount):
        invoice = super(SaleAdvancePaymentInvInherit, self)._create_invoice(
            order, so_line, amount
        )
        if invoice.invoice_line_ids:
            invoice._onchange_invoice_line_ids()
            invoice.sudo().write({"invoice_line_ids": invoice.invoice_line_ids})
            invoice._onchange_invoice_line_ids()

        return invoice
