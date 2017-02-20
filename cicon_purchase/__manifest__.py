{
    'name': 'CICON Material Request',
    'version': '0.1',
    'author': 'CICON',
    #'sequence': 99,
    'summary': 'CICON  Material Request',
    'description': """CICON  Material Request""",
    'website': 'http://www.cicon.net',
    'category': 'CICON IT',
    'depends': ['purchase_requisition','base'],
    'data': [
        'views/cicon_purchase_requisition_view.xml',
        'views/cicon_purchase_request_print_view.xml',
        'views/cicon_purchase_request_report.xml'
    ],
    'update_xml': [],
    'description': 'CICON Applications',
    'active': False,
    'installable': True,
    'application': False,
    'auto_install': False
}
