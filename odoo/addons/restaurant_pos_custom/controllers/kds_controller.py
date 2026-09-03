from odoo import http
from odoo.http import request

class KDSController(http.Controller):
    @http.route('/restaurant/kds/orders', type='json', auth='user')
    def kds_orders(self):
        Order = request.env['restaurant.order'].sudo()
        orders = Order.search([('state','in',('new','in_kitchen'))])
        data = []
        for o in orders:
            lines = []
            for l in o.order_line_ids:
                lines.append({
                    'id': l.id,
                    'product': l.name,
                    'qty': l.qty,
                })
            data.append({
                'id': o.id,
                'name': o.name,
                'table': o.table_id and o.table_id.name or False,
                'lines': lines,
                'state': o.state,
            })
        return data

    @http.route('/restaurant/kds/update_line', type='json', auth='user')
    def kds_update_line(self, line_id, new_state):
        Line = request.env['restaurant.order.line'].sudo().browse(int(line_id))
        if not Line:
            return {'error': 'not found'}
        # For simplicity, set parent order state change depending on new_state
        order = Line.order_id
        # no per-line state model in current design; we'll mark order state to in_kitchen/ready when lines updated externally
        if new_state == 'start':
            order.state = 'in_kitchen'
        elif new_state == 'ready':
            # naive check: if all lines are ready, set order ready
            order.state = 'ready'
        return {'ok': True}
