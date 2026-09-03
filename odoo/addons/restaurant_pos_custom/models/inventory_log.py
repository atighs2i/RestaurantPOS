from odoo import models, fields

class InventoryLog(models.Model):
    _name = 'restaurant.inventory.log'
    _description = 'Inventory Log'

    order_id = fields.Many2one('restaurant.order', string='Order')
    ingredient_id = fields.Many2one('product.product', string='Ingredient')
    quantity = fields.Float(string='Quantity')
    reference = fields.Char(string='Reference')
    message = fields.Text(string='Message')
    create_date = fields.Datetime(string='Created At', readonly=True)
