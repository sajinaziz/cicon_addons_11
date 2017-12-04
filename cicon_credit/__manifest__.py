{
    'name': 'CICON Credit Control',
    'version': '1.1',
    'author': 'CICON',
    'website': 'http://www.openerp.com',
    'category': 'Documents',
    'depends': ['base', 'cicon_partner_document', 'product', 'crm', 'account', 'contacts', 'sales_team'],
    'description': """Module for CICON Credit Management.""",
    'data': [
        'security/cicon_credit_security.xml',
        'security/ir.model.access.csv',
        'views/cicon_credit_application_view.xml'
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
}
