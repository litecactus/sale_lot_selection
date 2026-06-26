from odoo import models


class StockRule(models.Model):
    _inherit = 'stock.rule'

    def _get_stock_move_values(self, product_id, product_qty, product_uom,
                              location_dest_id, name, origin, company_id, values):
        move_values = super()._get_stock_move_values(
            product_id, product_qty, product_uom, location_dest_id, name,
            origin, company_id, values)
        if values.get('restrict_lot_ids'):
            move_values['restrict_lot_ids'] = values['restrict_lot_ids']
        return move_values
