{
    'name': 'CICON Credit Control',
    'version': '1.1',
    'author': 'CICON',
    'website': 'http://www.openerp.com',
    'category': 'Documents',
    'depends': ['base', 'cicon_partner_document', 'product', 'crm', 'account', 'contacts', 'sales_team',
                'cicon_sql_connect'],
    'description': """Module for CICON Credit Management.""",
    'data': [
        'security/cicon_credit_security.xml',
        'security/ir.model.access.csv',
        'views/cicon_credit_application_view.xml',
        'views/cicon_credit_reports.xml',
        'views/cicon_debtors_report.xml',
        'wizard/cicon_debtors_report_wizard_view.xml'
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
}
