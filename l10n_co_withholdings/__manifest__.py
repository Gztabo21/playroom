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
{
    "name": "Colombia Retenciones",
    "version": "14.0.0.0",
    "category": "account",
    "description": """
        Colombia Retenciones
    """,
    "author": "Brayhan Andres Jaramillo Castaño",
    "depends": ["account", "sale", "sale_discount_display_amount", "purchase"],
    "data": [
        "security/ir.model.access.csv",
        "views/account_base_tax_view.xml",
        "views/account_tax_view_inherit.xml",
        "views/account_move_tax_view.xml",
        "views/account_move_inherit_view.xml",
        "views/sale_order_view_inherit.xml",
        "views/purchase_order_view_inherit.xml",
    ],
    "demo": [],
    "installable": True,
    "auto_install": False,
}
