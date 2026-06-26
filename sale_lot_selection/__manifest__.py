{
    'name': 'Sale Order Lot/Serial Selection',
    'version': '19.0.1.0.0',
    'sequence': 60,
    'category': 'Inventory/Sales',
    'author': 'FIZZY PROJECTS LTD',
    'maintainer': 'https://github.com/litecactus/',
    'website': 'https://www.fizzyprojects.com',
    'support': 'alex@fizzyprojects.com',
    'summary': 'Pick exact lot/serial numbers on a sale order line and force the '
               'delivery to reserve them, using the native reservation engine.',
    'description': """
Sale Order Lot/Serial Selection
===============================

Lets a salesperson choose specific lot/serial numbers on a sale order line.
The chosen lots ride the procurement down onto the delivery move as a
reservation restriction (mirroring the native ``restrict_partner_id``
mechanism), and ``_action_assign`` is steered to reserve exactly those lots
through the standard ``_update_reserved_quantity`` path.

Unlike a post-confirmation move-line rewrite, this does not delete and recreate
move lines: it restricts the engine's input and lets core do the reservation,
so partial availability, backorders, unreserve and traceability all keep working.
""",
    'depends': ['sale_stock', 'stock'],
    'data': [
        'views/sale_order_line_views.xml',
        'views/stock_picking_views.xml',
    ],
    'images': ['static/description/banner.png'],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
