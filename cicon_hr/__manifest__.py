{
    'name' : 'CICON HR',
    'version': '1.1',
    'author' : 'OpenERP SA',
    'website' : 'http://www.openerp.com',
    'category': 'Human Resource',
    'depends' : ['hr'],
    'description': """
Module for CICON HR Employee Attendance(Time Punch).
===============================================
    """,
    'data': [ 'security/cicon_hr_security.xml',
              'security/ir.model.access.csv',
              'views/cicon_hr_view.xml',
              'views/cicon_hr_attendance_view.xml',
              'wizard/import_attendance.xml' ,
              'views/cicon_hr_leave_view.xml',
              'views/daily_attendance_report.xml',
              'views/employee_attendance_report.xml',
              'views/employee_leave_report.xml',
              'views/cicon_attendance_report.xml',
              'wizard/emp_attendance_wizard_view.xml',
              'wizard/process_attendance_view.xml'],
    'demo': [],
    'installable': True,
    'auto_install': False,
}