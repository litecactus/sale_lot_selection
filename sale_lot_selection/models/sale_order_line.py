from odoo import api, fields, models
from odoo.exceptions import ValidationError


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    available_lots = fields.Many2many(
        'stock.lot', compute='_compute_available_lots',
        string='Available Serial Numbers')
    lot_ids = fields.Many2many(
        'stock.lot', relation='sale_order_line_lot_rel',
        column1='sol_id', column2='lot_id', string='Lot/Serial Numbers',
        domain="[('id', 'in', available_lots)]",
        help="Specific lot/serial numbers to reserve for this line. The "
             "delivery will reserve exactly these.")

    @api.depends('product_id', 'order_id.warehouse_id')
    def _compute_available_lots(self):
        Quant = self.env['stock.quant']
        for line in self:
            location = line.order_id.warehouse_id.lot_stock_id
            if not line.product_id or line.product_id.tracking == 'none' or not location:
                line.available_lots = False
                continue
            # Reuse the native gather so the offered lots are exactly what the
            # reservation engine could pick, with unreserved stock on hand.
            quants = Quant._gather(line.product_id, location)
            line.available_lots = quants.filtered(
                lambda q: q.lot_id and q.available_quantity > 0).lot_id

    @api.onchange('lot_ids')
    def _onchange_lot_ids_qty(self):
        # For serials each chosen lot is one unit, so keep demand in step.
        for line in self:
            if line.lot_ids and line.product_id.tracking == 'serial':
                line.product_uom_qty = len(line.lot_ids)

    @api.constrains('lot_ids', 'product_uom_qty', 'product_id')
    def _check_serial_lot_count(self):
        for line in self:
            if (line.product_id.tracking == 'serial' and line.lot_ids
                    and len(line.lot_ids) != int(line.product_uom_qty)):
                raise ValidationError(self.env._(
                    "For serial-tracked product '%(product)s' the number of "
                    "selected serials (%(lots)s) must match the ordered "
                    "quantity (%(qty)s).",
                    product=line.product_id.display_name,
                    lots=len(line.lot_ids),
                    qty=int(line.product_uom_qty),
                ))

    def _prepare_procurement_values(self):
        values = super()._prepare_procurement_values()
        if self.lot_ids:
            values['restrict_lot_ids'] = [fields.Command.set(self.lot_ids.ids)]
        return values

    def write(self, vals):
        res = super().write(vals)
        if 'lot_ids' in vals or 'product_uom_qty' in vals:
            for line in self.filtered(lambda l: l.order_id.state == 'sale'):
                moves = line.move_ids.filtered(
                    lambda m: m.state not in ('done', 'cancel'))
                if not moves:
                    continue
                moves.write({
                    'restrict_lot_ids': [fields.Command.set(line.lot_ids.ids)]})
                moves._do_unreserve()
                moves._action_assign()
        return res
