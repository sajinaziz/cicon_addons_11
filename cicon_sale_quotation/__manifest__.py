{
    'name': 'CICON Sale Quotation',
    'version': '11.1',
    'author': 'CICON',
    'website': 'http://www.odoo.com',
    'category': 'sale',
    'depends': ['sale'],
    'description': """Module for CICON Sale Management.""",
    'data': [
        'views/cicon_sale_view.xml',
        'views/cicon_sale_reports.xml',
        'views/cicon_sale_report_template.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
}
