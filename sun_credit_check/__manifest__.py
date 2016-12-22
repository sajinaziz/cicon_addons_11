{
    'name': 'Sun System Credit Check',
    'version': '1.1',
    'author': 'CICON',
    'category': 'Generic Modules/Other',
    'description': """
        Module for the Checking the Credits in Sun System on customer and projects.  Multiple suncode on both projects and customer will support.
    """,
    'website': 'http://www.openerp.com',
    'depends': ['base','uae_check','project'],
    "data": ["security/ir.model.access.csv",
             "views/sun_credit_check_view.xml",
             #"views/sun_credit_check_report.xml",
             #"views/credit_check_print.xml"
             ],
    'test': [],
    'installable': True,
    'active': False,
}
