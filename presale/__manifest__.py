#   coding: utf-8
##############################################################################
#
#   Copyright (C) 2022 Odoo Inc
#   Autor: Brayhan Andres Jaramillo Castaño
#   Correo: brayhanjaramillo@hotmail.com
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    "name": "Presale",
    "version": "14.0.0.0.1",
    "category": "sale",
    "author": "Brayhan Andres Jaramillo Castaño",
    "summary": "sale",
    "website": "",
    "depends": [
        "sale",
        "website_save_cart",
        "product_brand",
        "wt_product_seller",
        "website",
        "product_visibility_website",
        "product_brand",
        "website_quick_quotation_inherit",
    ],
    "data": [
        "data/config_parameter_data.xml",
        "data/ir_attachment_data.xml",
        "views/register_attendance_presale_template.xml",
        "data/website_menu_data.xml",
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/assest.xml",
        "views/sale_order_inherit_view.xml",
        "views/website_template_inherit.xml",
        "views/res_partner_inherit_view.xml",
        "views/attendence_presale_view.xml",
        "views/menu.xml",
    ],
    "demo": [],
    "installable": True,
    "auto_install": False,
}
