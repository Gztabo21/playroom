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
    "name": "Pre Sale",
    "version": "14.0.0.0.1",
    "category": "sale",
    "author": "Brayhan Andres Jaramillo Castaño",
    "summary": "sale",
    "website": "",
    "depends": ["sale", "website_save_cart", "product_brand"],
    "data": [
        "data/config_parameter_data.xml",
        "security/security.xml",
        "views/sale_order_inherit_view.xml",
        "views/website_template_inherit.xml",
        "views/res_partner_inherit_view.xml",
        "views/menu.xml",
    ],
    "demo": [],
    "installable": True,
    "auto_install": False,
}
