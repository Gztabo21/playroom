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


class AccountBaseTax(models.Model):
    _name = "account.base.tax"
    _description = "Account Base Tax"

    TYPE_TAX = [("general", "General"), ("line", u"Línea")]

    tax_id = fields.Many2one("account.tax", string="Tax related")
    start_date = fields.Date(string="Date From", required=True)
    end_date = fields.Date(string="Date To", required=True)
    amount = fields.Float(string="Amount", default=0, required=True)
    type_tax = fields.Selection(
        TYPE_TAX, string="Scope", default="general", required=True
    )
    is_active = fields.Boolean(string="Activo", default=False)
