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
from odoo import fields, models, api


class ResPartnerInherit(models.Model):
    _inherit = "res.partner"

    brand_ids = fields.Many2many(
        "product.brand",
        "res_partner_product_brand_rel",
        column1="partner_id",
        column2="brand_id",
        string="Marcas",
    )
