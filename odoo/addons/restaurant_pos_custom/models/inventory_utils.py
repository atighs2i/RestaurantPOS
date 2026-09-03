from odoo import api, models, _
from odoo.exceptions import UserError

class InventoryUtils(models.AbstractModel):
    _name = 'restaurant.inventory'
    _description = 'Inventory Utilities'

    @api.model
    def create_outgoing_picking_for_order(self, order):
        StockPicking = self.env['stock.picking']
        StockMove = self.env['stock.move']
        Warehouse = self.env['stock.warehouse']

        # find default warehouse and picking type
        warehouse = Warehouse.search([], limit=1)
        picking_type = self.env['stock.picking.type'].search([('code','=','outgoing')], limit=1)
        if not picking_type:
            raise UserError(_('No outgoing picking type found.'))

        moves_vals = []
        uom_unit = self.env.ref('uom.product_uom_unit')

        for line in order.order_line_ids:
            # find recipes for the product
            recipes = self.env['restaurant.recipe'].search([('product_id','=',line.product_id.id)])
            for r in recipes:
                qty = r.quantity * line.qty
                if qty <= 0:
                    continue
                src_loc = picking_type.default_location_src_id and picking_type.default_location_src_id.id or (warehouse.lot_stock_id and warehouse.lot_stock_id.id)
                dest_loc = picking_type.default_location_dest_id and picking_type.default_location_dest_id.id or self.env.ref('stock.stock_location_customers').id
                move = {
                    'name': (r.ingredient_id.name or '')[:200],
                    'product_id': r.ingredient_id.id,
                    'product_uom_qty': qty,
                    'product_uom': (r.ingredient_id.uom_id and r.ingredient_id.uom_id.id) or uom_unit.id,
                    'picking_type_id': picking_type.id,
                    'location_id': src_loc,
                    'location_dest_id': dest_loc,
                }
                moves_vals.append(move)

        if not moves_vals:
            # nothing to consume
            return False

        picking_vals = {
            'picking_type_id': picking_type.id,
            'origin': order.name,
        }
        picking = StockPicking.create(picking_vals)

        for mv in moves_vals:
            mv.update({'picking_id': picking.id})
            StockMove.create(mv)

        # confirm and assign
        picking.action_confirm()
        try:
            picking.action_assign()
        except Exception:
            # log and continue
            self.env['restaurant.inventory.log'].create({
                'order_id': order.id,
                'message': 'Could not assign picking automatically.'
            })

        # try to validate (transfer)
        try:
            picking.button_validate()
        except Exception as e:
            # Validation may fail if not enough stock; log warning
            self.env['restaurant.inventory.log'].create({
                'order_id': order.id,
                'message': 'Validation failed: %s' % str(e)
            })

        # create inventory logs for moves
        for move in picking.move_lines:
            self.env['restaurant.inventory.log'].create({
                'order_id': order.id,
                'ingredient_id': move.product_id.id,
                'quantity': -move.product_uom_qty,
                'reference': picking.name,
            })

        return picking
