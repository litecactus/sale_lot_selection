from odoo import fields, models


class StockMove(models.Model):
    _inherit = 'stock.move'

    restrict_lot_ids = fields.Many2many(
        'stock.lot', relation='stock_move_restrict_lot_rel',
        column1='move_id', column2='lot_id', string='Restrict Serial Numbers',
        help="If set, reservation of this move is restricted to these "
             "lot/serial numbers (chosen on the sale order line).")

    def _prepare_merge_moves_distinct_fields(self):
        # Moves carrying different chosen serials must never be merged.
        return super()._prepare_merge_moves_distinct_fields() + ['restrict_lot_ids']

    def _action_assign(self, force_qty=False):
        # Reserve the salesperson's chosen lots first, through the native
        # reservation path, before core does its FIFO assignment for anything
        # left over. This keeps reserved_quantity accounting correct.
        restricted = self.filtered(
            lambda m: m.restrict_lot_ids and not m.picked
            and m.state not in ('done', 'cancel', 'draft'))
        for move in restricted:
            rounding = move.product_id.uom_id
            need = move.product_qty - sum(
                move.move_line_ids.mapped('quantity_product_uom'))
            for lot in move.restrict_lot_ids:
                if rounding.compare(need, 0) <= 0:
                    break
                taken = move._update_reserved_quantity(
                    need, move.location_id, lot_id=lot, strict=True)
                need -= taken
        return super()._action_assign(force_qty)
