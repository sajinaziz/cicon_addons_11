{
    'name': 'CICON Payment Followup',
    'version': '1.1',
    'author': 'CICON',
    'category': 'Others',
    'description': """
Module for the CICON Payment Followup.
================================================
    """,
    'website': 'http://www.cicon.ae',
    # 'depends' : ['project_gtd','account_followup'],
    'depends': ['project','account'],
    "data":["views/cic_project_task_view.xml","views/cic_project_task_data.xml"],
    'test': [],
    'installable': True,
    'active': False,
}
