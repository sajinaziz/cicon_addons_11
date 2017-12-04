{
    'name': 'CICON Document',
    'version': '1.1',
    'author': 'CICON',
    'website': 'http://www.openerp.com',
    'category': 'Documents',
    'depends': ['base', 'document'],
    'description': """Module for CICON Document Management.""",
    'data': [
        'security/cicon_document_security.xml',
        'security/ir.model.access.csv',
        'views/cicon_document_view.xml'
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
}
