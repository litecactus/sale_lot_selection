# Sale Order Lot/Serial Selection

Odoo 19 add-on that lets a salesperson pick specific lot/serial numbers on a
sale order line and forces the resulting delivery to reserve exactly those
serials.

## Why

Natively Odoo decides which serials ship at reservation time, using the removal
strategy (FIFO by default). The salesperson has no say. This module lets the
choice be made on the quotation and carries it down to the delivery.

## How it works

It does **not** delete and recreate move lines after confirmation. Instead it
restricts the reservation engine's input, mirroring the native
`restrict_partner_id` mechanism:

1. `sale.order.line` gains a `lot_ids` field, with available lots computed from
   the native `stock.quant._gather` so only genuinely reservable serials are offered.
2. The chosen lots propagate through `_prepare_procurement_values` and
   `stock.rule._get_stock_move_values` onto the delivery move as `restrict_lot_ids`.
3. `stock.move._action_assign` reserves those lots first via the standard
   `_update_reserved_quantity` path, then core handles anything left over.

Because reservation goes through the native path, partial availability,
backorders, unreserve and traceability all keep working.

The Serial/Lot column is also shown by default on the delivery's Operations list.

## Install

Drop `sale_lot_selection` into your addons path and install it.

```bash
odoo-bin -d <db> -i sale_lot_selection --stop-after-init
```

## Requirements

Odoo 19 (Community or Enterprise). Depends on `sale_stock` and `stock`.

## License

LGPL-3.

## Support

FIZZY PROJECTS LTD &middot; hello@fizzyprojects.com &middot; https://www.fizzyprojects.com
