{
    'name': 'CICON Product Group',
    'version': '1.1',
    'author': 'OpenERP SA',
    'website': 'http://www.openerp.com',
    'category': 'CICON Product Group',
    'depends': ['base','product'],
    'description': """
Module for CICON Product Group Template.
===============================================
    """,
    'data': [
        'security/ir.model.access.csv',
        'views/cicon_prod_group_view.xml'],
    'demo': [],
    'installable': True,
    'auto_install': False,
}