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
import logging
_logger = logging.getLogger(__name__)
import time


class ResPartnerInherit(models.Model):
    _inherit = "res.partner"

    @api.model
    def get_data_products(self,partner_id):
        partner_id = self.env["res.partner"].sudo().search([("id", "=", partner_id)], limit=1)
        pricelist_id = partner_id.property_product_pricelist
        if not pricelist_id:
            pricelist_id = self.env.ref("product.list0", False)
        # self.env.cr.execute("""
        #         SELECT 
        #             pp.id as id,
        #             pt.name as name,
        #             concat(uom.id,uom.name) as uom_id
        #         FROM
        #             product_product as pp
        #         join product_template pt on pp.product_tmpl_id = pt.id
        #         join uom_uom uom on pt.uom_id = uom.id
        # """)
        # pp = self.env.cr.dictfetchall()
        products = self.env["product.product"].search([])
        data = []
        _logger.info('inicia')
        inii = time.perf_counter()
        print(inii)
        for record in products:
            # product = self.env["product.product"].search([('id','=',record['id'])],limit=1)
            price = pricelist_id.get_product_price(record, 1, partner_id)

            data.append(
                {
                    "id": record.id,
                    "name": '%s - <span class="badge">%s</span>'
                    % (record.display_name, record.outgoing_qty),
                    "uom_id": (record.uom_id.id, record.uom_id.name),
                    "price": price,
                    "total": price,
                }
            )
        fin = time.perf_counter()
        print(f"Duracion {inii-fin :0.4f}")
        return data
    
    @api.model
    def get_partners_all(self):
        self.env.cr.execute("""
        select 
            id,
            name,
            phone
        FROM res_partner;
        """)
        partners = self.env.cr.dictfetchall()
        return partners