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
from datetime import date, datetime
from odoo.exceptions import Warning, UserError, ValidationError


class SaleOrderInherit(models.Model):
    _inherit = "sale.order"

    pre_sale = fields.Boolean(string="¿Es Preventa?", default=False)
    laboratory_id = fields.Many2one("res.partner", "Laboratorio", readonly=True)

    @api.model_create_multi
    def create(self, vals):
        context = self.env.context
        if "pre_sale" in context:
            vals[0].update({"pre_sale": True})
        res = super(SaleOrderInherit, self).create(vals)
        return res

    def validate_pre_sale(self):
        """
        Permite validar si esta activo o no la preventa
        """
        pre_sale_date_from = (
            self.env["ir.config_parameter"].sudo().with_company(self.env.company.id)
        ).get_param("pre_sale_date_from")

        pre_sale_date_to = (
            self.env["ir.config_parameter"].sudo().with_company(self.env.company.id)
        ).get_param("pre_sale_date_to")

        today = datetime.today().date()

        pre_sale_date_from = datetime.strptime(pre_sale_date_from, "%Y-%m-%d").date()
        pre_sale_date_to = datetime.strptime(pre_sale_date_to, "%Y-%m-%d").date()

        if (today >= pre_sale_date_from) and (today <= pre_sale_date_to):
            return True

        return False

    def action_confirm(self):
        if self.validate_pre_sale():
            if not self.user_has_groups("pre_sale.group_confirm_sale"):
                raise ValidationError(
                    "Todavia no es posible confirma la orde de venta."
                )
        res = super(SaleOrderInherit, self).action_confirm()
        return res
