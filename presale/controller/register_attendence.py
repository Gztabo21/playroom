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

from odoo import http
from odoo.http import request


class RegisterAttendecePresale(http.Controller):
    @http.route("/register/presale/", auth="public", website=True, type="http")
    def register_presale(self, **kwargs):
        print("*****")
        print("entramos")
        print(kwargs)
        print(self)
        print(request.env.context)
        result = {
            "success": "",
            "error": "",
        }
        if "vat" in kwargs:
            vat = kwargs["vat"]
            result = request.env["res.partner"].search_partner_by_vat(vat)

        return http.request.render(
            "presale.register_attendence_template", {"result": result}
        )

    # @http.route("/register/presale/subimit", auth="public", website=True, type="http")
    # def register_presale_submit(self, **kwargs):
    #     print("*****")
    #     print("entramos")
    #     print(kwargs)
    #     return http.request.render(
    #         "presale.register_attendence_success_template", {"teachers": []}
    #     )
