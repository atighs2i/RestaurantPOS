from odoo import models, fields, api, _
from odoo.exceptions import UserError

class RestaurantOrder(models.Model):
    _name = 'restaurant.order'
    _description = 'Restaurant Order'

    name = fields.Char(string='Order Reference', required=True, copy=False, readonly=True, default='New')
    date_order = fields.Datetime(string='Order Date', default=fields.Datetime.now)
    state = fields.Selection([('new','New'),('in_kitchen','In Kitchen'),('ready','Ready'),('served','Served'),('paid','Paid')], default='new')
    order_line_ids = fields.One2many('restaurant.order.line','order_id',string='Order Lines')
    table_id = fields.Many2one('restaurant.table',string='Table')
    total_amount = fields.Float(string='Total', compute='_compute_total')

    @api.depends('order_line_ids.price_subtotal')
    def _compute_total(self):
        for rec in self:
            rec.total_amount = sum(line.price_subtotal for line in rec.order_line_ids)

    def button_set_paid(self):
        for order in self:
            order.state = 'paid'
            try:
                # call inventory consumption utility
                self.env['restaurant.inventory'].create_outgoing_picking_for_order(order)
            except Exception as e:
                # log the exception to inventory log and continue (default behavior: allow payment but flag)
                self.env['restaurant.inventory.log'].create({
                    'order_id': order.id,
                    'message': 'Inventory consumption error: %s' % str(e)
                })

class RestaurantOrderLine(models.Model):
    _name = 'restaurant.order.line'
    _description = 'Order Line'

    order_id = fields.Many2one('restaurant.order', string='Order')
    product_id = fields.Many2one('product.product', string='Product')
    name = fields.Char(related='product_id.name', string='Product Name', store=True)
    qty = fields.Float(string='Quantity', default=1.0)
    price_unit = fields.Float(string='Unit Price', related='product_id.lst_price', store=True)
    price_subtotal = fields.Float(string='Subtotal', compute='_compute_subtotal')

    @api.depends('qty','price_unit')
    def _compute_subtotal(self):
        for line in self:
            line.price_subtotal = line.qty * line.price_unit
