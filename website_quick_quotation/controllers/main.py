
from odoo import fields, http, _
from odoo.http import request
from odoo.exceptions import AccessError, MissingError

class WebsiteQuickQuotation (http.Controller):
    
    @http.route('/website_quick_quotation/get_products_data', type='json', auth='public', website=True)
    def get_products_data(self, **kw):
        products = request.env['product.product'].sudo().search_read([], ['name', 'id' , 'uom_id'])
        return products
    
    @http.route('/website_quick_quotation/submit_quotation', type='json', auth='public', website=True)
    def submit_quotation(self, data, name,  email, **kw):
        lines = []
        if not name or not email or not data:
            return
        
        partner_sudo = request.env['res.partner'].sudo()
        sale_sudo = request.env['sale.order'].sudo()
        
        partner = partner_sudo.search([('email', '=', email)], limit=1)
        if (not partner):
            partner = partner_sudo.create({
                'company_type' : 'person',
                'name' : name,
                'email' : email,
            })
        
        for d in data:
            val= {
                'product_id': d['product_id'],
                'product_uom_qty': d['qty'],
            }
            lines.append((0,0,val))
            
        vals = {
            'partner_id': partner.id,
            'order_line': lines,
        }
        sale_order = sale_sudo.create(vals)       
        return sale_order.id