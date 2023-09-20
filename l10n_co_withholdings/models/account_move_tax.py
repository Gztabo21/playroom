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
from odoo import api, models, fields, _


class AccountMoveTax(models.Model):
    _name = "account.move.tax"
    _description = "Account Move Tax"

    move_id = fields.Many2one(
        "account.move", string="Invoice", ondelete="cascade", index=True
    )
    name = fields.Char(string="Tax Description", required=True)
    tax_id = fields.Many2one("account.tax", string="Tax", ondelete="restrict")
    account_id = fields.Many2one(
        "account.account",
        string="Cuenta",
        required=True,
        domain=[("deprecated", "=", False)],
    )
    amount = fields.Monetary("Importe")
    sequence = fields.Integer(
        help="Gives the sequence order when displaying a list of invoice tax."
    )
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        related="account_id.company_id",
        store=True,
        readonly=True,
    )
    currency_id = fields.Many2one(
        "res.currency", related="move_id.currency_id", store=True, readonly=True
    )
    base = fields.Monetary(string="Base", required=True)

    def _compute_amount_total(self):
        for tax_line in self:
            tax_line.amount_total = tax_line.amount
