{
    'name': 'CICON Sun Accounting',
    'version': '1.1',
    'author': 'CICON',
    'category': 'Others',
    'description': """
    Sun System Integration
    """,
    'website': 'http://www.openerp.com',
    'depends': ['account'],
    "data": ["security/ir.model.access.csv", "views/cic_sun_system_view.xml"],
    'test': [],
    'installable': True,
    'active': False,
}
