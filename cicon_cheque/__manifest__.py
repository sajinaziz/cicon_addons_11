{
    'name': 'CICON Cheque',
    'version': '1.1',
    'author': 'CICON',
    'website': 'http://www.openerp.com',
    'category': 'Finance',
    'depends': ['base', 'account'],
    'description': """CICON Cheque Management.""",
    'data': [
     'views/cicon_cheque_view.xml',
     'report/cicon_cheque_report.xml',
     'report/cicon_cheque_report_template.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
}
