from odoo import models, fields

class Recipe(models.Model):
    _name = 'restaurant.recipe'
    _description = 'Recipe - link between product and ingredients'

    product_id = fields.Many2one('product.product', string='Menu Item', required=True)
    ingredient_id = fields.Many2one('product.product', string='Ingredient', required=True)
    quantity = fields.Float(string='Quantity', default=0.0)
