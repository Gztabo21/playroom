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
from datetime import date, datetime
from odoo.exceptions import Warning, UserError, ValidationError


class SaleOrderInherit(models.Model):
    _inherit = "sale.order"

    presale = fields.Boolean(string="¿Es Preventa?", default=False)
    laboratory_id = fields.Many2one("res.partner", "Laboratorio", readonly=True)

    @api.model_create_multi
    def create(self, vals):
        context = self.env.context
        if "presale" in context:
            vals[0].update({"presale": True})
        res = super(SaleOrderInherit, self).create(vals)
        return res

    def validate_presale(self):
        """
        Permite validar si esta activo o no la preventa
        """
        print("Entramos")
        presale_date_from = (
            self.env["ir.config_parameter"].sudo().with_company(self.env.company.id)
        ).get_param("presale_date_from")

        presale_date_to = (
            self.env["ir.config_parameter"].sudo().with_company(self.env.company.id)
        ).get_param("presale_date_to")

        today = datetime.today().date()

        presale_date_from = datetime.strptime(presale_date_from, "%Y-%m-%d").date()
        presale_date_to = datetime.strptime(presale_date_to, "%Y-%m-%d").date()

        if (today >= presale_date_from) and (today <= presale_date_to):
            return True

        return False

    def action_confirm(self):
        if self.validate_presale():
            if not self.user_has_groups("presale.group_confirm_sale"):
                raise ValidationError(
                    "Todavia no es posible confirma la orde de venta."
                )
        res = super(SaleOrderInherit, self).action_confirm()
        return res

    def update_presale(self):
        if self.validate_presale():
            self.sudo().write({"presale": True})
