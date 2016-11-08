{
    "name": "CMMS",
    "version": "0.1",
    'summary': 'Maintenance, Repair and Operation',
    'description': """
Manage Maintenance process in OpenERP
=====================================

Machine Maintenance, Repair and Operation.
Support Breakdown Maintenance and Preventive Maintenance.

Main Features
-------------
    * Service/Maintenance Management
    * Maintenance Job Orders Management
    * Parts Management
    * Tasks Management (Standard job)

Required modules:
    * base
    * purchase
    * Accounting

    """,
    "author": "@ CICON",
    "website": "http://www.cicondubai.ae/",
    "category": "Enterprise Maintenance Management System",
    "depends": ['base', 'product', 'mail', 'stock'],
    "data": [
        'security/cmms_security.xml',
        'security/ir.model.access.csv',
        'views/cmms_machine_view.xml',
        'views/cmms_report.xml',
        'views/cmms_header.xml',
        'views/report_machine_status.xml',
        'views/pm_sch_plan_report.xml',
        'views/job_order_form_view.xml',
        'views/inventory_expense_reports.xml',
        'views/job_order_report.xml',
        'views/report_machine_summary.xml',
        'views/report_partsby_producttype_summary.xml',
        'views/report_machine_analysis_summary.xml',
        'views/cmms_store_view.xml',
        'views/cmms_joborder_view.xml',
        'views/pm_task_view.xml',
        'views/cmms_joborder_sequence.xml',
        'wizard/pm_job_generate_view.xml',
        'wizard/job_order_generate_view.xml',
        'wizard/pm_task_sch_report_wizard_view.xml',
        'wizard/spare_part_type_wizard_view.xml',
        'wizard/common_report_wizard_view.xml',
        'views/report_machine_preventive_status.xml',
        # 'wizard/consume_product_wizard_view.xml',
        'views/cmms_report.xml'],
    "init_xml": [],
    'update_xml': [],
    "demo_xml": [],
    "active": False,
    "installable": True,
    "application": True
}
