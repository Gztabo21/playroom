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
    "name": "Quick quotation Inherit",
    "version": "14.0.0.0.1",
    "category": "sale",
    "author": "Brayhan Andres Jaramillo Castaño",
    "summary": """
        This module allows your clients and website visitors to generate quotations by filling out a products form from website and submitting it.
        """,
    "website": "",
    "depends": [
        "base",        
        "sale_management",
        "website",
        "website_quick_quotation",
    ],
    "data": [
        "data/website_menu_data.xml",
        "views/assest.xml",
        # "security/ir.model.access.csv",
        "views/website_quick_quotation_inherit_template.xml",
    ],
    "demo": [],
    "installable": True,
    "auto_install": False,
}
