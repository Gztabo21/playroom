from odoo import fields, models, api, _
from odoo.exceptions import UserError


class PromotionScheme(models.Model):
    _name = "promotion.scheme"
    _description = "Promotion Scheme"

    name = fields.Char(string="Scheme Name")
    applicable_on = fields.Selection(
        [("product", "Product"), ("product_category", "Product Category")],
        default="product",
    )
    product_id = fields.Many2one("product.product", string="Product")
    product_category_id = fields.Many2one("product.category", string="Product Category")
    product_qty = fields.Float("Minimum Qty")
    promotion_line_ids = fields.One2many(
        "promotion.scheme.line", "promotion_id", string="Rewarded Lines"
    )
    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")

    @api.onchange("product_qty")
    def onchange_product_qty(self):
        if self.product_qty <= 0.0:
            pass
            # raise UserError(_('Please enter minimum qty grater than 0.'))


class PromotionSchemeLine(models.Model):
    _name = "promotion.scheme.line"
    _description = "Promotion Scheme Line"

    promotion_id = fields.Many2one("promotion.scheme", string="Promotion Scheme")
    reward_product_id = fields.Many2one("product.product", string="Reward Product")
    reward_product_qty = fields.Float("Reward Qty")
    reward_product_uom_id = fields.Many2one("uom.uom", string="Product uom")

    @api.onchange("reward_product_id")
    def onchange_method(self):
        self.reward_product_uom_id = self.reward_product_id.uom_id.id
