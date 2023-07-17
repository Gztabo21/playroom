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
import time
from odoo import models, api, fields, _
from odoo.exceptions import UserError


class PurchaseOrderInherit(models.Model):
    _inherit = "purchase.order"

    def action_multi_product(self):
        """
        Permite abrir el wizard para agregar los productos
        """
        context = self.env.context.copy()
        context.update({"purchase_id": self.id})
        self.env.context = context
        vals = {
            "name": _(u"Selección de Productos"),
            "res_model": "multi.product.select",
            "type": "ir.actions.act_window",
            "view_id": self.env.ref(
                "multi_product_po.purchase_multi_product_select_view_form"
            ).id,
            "view_type": "form",
            "view_mode": "form",
            "target": "new",
            "nodestroy": True,
            "context": context,
        }
        return vals


PurchaseOrderInherit()
