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

from odoo import fields, models, api


class ResPartnerInherit(models.Model):
    _inherit = "res.partner"

    FILTER_MODE = [("brand_only", "Por Marca")]

    filter_mode = fields.Selection(selection_add=FILTER_MODE)
    website_available_brand_ids = fields.Many2many(
        "product.brand",
        "res_partner_product_brand_visibility_rel",
        column1="partner_id",
        column2="brand_id",
        string="Marcas Disponibles",
        help="Marcas disponibles en el sitio web",
    )

    def search_partner_by_vat(self, vat: str) -> bool:
        """
        Allow create attendece presale

        Args: vat str: Identitication partner
        """
        result = {
            "success": "",
            "error": "",
        }
        if vat:
            partner_id = (
                self.env["res.partner"].sudo().search([("vat", "like", vat)], limit=1)
            )
            if partner_id:
                attendance_id = (
                    self.env["attendance.presale"]
                    .sudo()
                    .search([("partner_id", "=", partner_id.id)], limit=1)
                )
                if attendance_id:
                    result["error"] = (
                        "El cliente <strong>%s</strong> identificado con <strong>%s</strong>, ya ha realizado el registro de asistencia anteriormente."
                        % (partner_id.name, partner_id.vat)
                    )
                else:
                    res = (
                        self.env["attendance.presale"]
                        .sudo()
                        .create({"partner_id": partner_id.id})
                    )
                    if res:
                        result[
                            "success"
                        ] = """
                        Cliente <strong>%s</strong> identificado con <strong>%s</strong>.
                        Ha completado el Registro de asistencia con éxito. <br/> 
                        
                        """ % (
                            partner_id.name,
                            partner_id.vat,
                        )
            else:
                result["error"] = (
                    "El cliente con identificación <strong>%s</strong>, no se encontra registrado en el sistema"
                    % (vat)
                )
        return result

    @api.onchange("filter_mode")
    def onchange_filter_mod(self):
        self.website_available_cat_ids = None
        self.website_available_product_ids = None
        self.website_available_brand_ids = None

    @api.onchange("website_available_brand_ids")
    def onchange_brand_ids(self):
        self.website_available_product_ids = None
        if self.filter_mode == "brand_only":
            product_ids = (
                self.env["product.template"]
                .sudo()
                .search(
                    [("product_brand_id", "in", self.website_available_brand_ids.ids)]
                )
            )
            if product_ids:
                self.website_available_product_ids = [(6, 0, product_ids.ids)]
