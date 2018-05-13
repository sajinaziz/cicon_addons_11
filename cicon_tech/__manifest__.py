{
    'name': 'CICON Submittal',
    'version': '0.1',
    'author': 'CICON',
    'website': 'http://www.ciconuae.net',
    'category': 'Generic Modules/Others',
    'depends': ['project', 'res_company_extn', 'cicon_user_sign','cicon_job_site'],
    'data': ['security/tech_security.xml',
             'security/ir.model.access.csv',
             'wizard/drawing_creator_view.xml',
             'views/project_view.xml',
             'views/tech_submittal_revision_view.xml',
             'views/tech_submittal_view.xml',
             'views/report.xml',
             'views/report.xml',
             'views/drawing_type_data.xml',
             'report/drawing_register_view.xml',
             'views/config_tree_view.xml',
             'report/submittal_print_view.xml',
             'views/tech_submittal_dashboard.xml',
             'views/cicon_tech_view.xml',
             'views/tech_submittal_doc_view.xml',
             'wizard/document_revision_wizard_view.xml',
             'views/submittal_email.xml',
            ],
    'update_xml': [],
    'description': 'Cicon Modules', 'active': False, 'installable': True, 'application': False, 'auto_install': False
}