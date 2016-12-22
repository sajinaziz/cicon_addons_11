from odoo import models,fields,api
from odoo.tools.translate import _
import datetime


class Task(models.Model):
    _inherit = 'project.task'

    # _columns = {
    #     'project_id': fields.many2one('project.project', 'Project',  ondelete='set null', select="1", track_visibility='onchange'),
    #     'sales_person_id':fields.related('project_id', 'sales_person_id', type='many2one',relation='res.users', string="Project Sales Person"),
    #     'customer_sales_person_id': fields.related('partner_id', 'user_id', type='many2one',relation='res.users', string="Customer Sales Person"),
    #     'customer_payment_term': fields.related('partner_id', 'property_payment_term',relation='account.payment.term', type='many2one',string="Customer Payment Term"),
    #     'total_amount': fields.float("Total Amount", digits=(10,2)),
    #
    #
    #     #Modified for Filter By Customer
    #     # Payment Follow up
    #
    #    #'due_date': fields.date("Expected Payment Date"),
    # }

    project_id = fields.Many2one('project.project', 'Project', ondelete='set null', select="1",
                                  track_visibility='onchange')
    sales_person_id = fields.Many2one('res.users',string='Project Sales Person')
    customer_sales_person_id = fields.Many2one('res.users',string='Customer Sales Person')
    customer_payment_term = fields.Many2one('account.payment.term',string='Customer Payment Term')
    total_amount = fields.Float("Total Amount", digits=(10, 2))
    work_ids = fields.One2many('project.task.work','task_id', string="Works")

    # def change_partner(self, cr, uid, ids, partner_id, context=None):
    #     res = {}
    #     _val = {'project_id': None,'customer_sales_person_id':None,'customer_payment_term':None}
    #     _domain = {}
    #     _domain['customer_sales_person_id'] = []
    #     _domain['customer_payment_term'] = []
    #     if partner_id:
    #         res = self.pool.get('res.partner').read(cr, uid, partner_id, ['user_id','property_payment_term'], context=context)
    #         if res['user_id']:
    #             _val.update({'customer_sales_person_id': res['user_id'][0]})
    #             _domain['customer_sales_person_id'] = [('id','=',res['user_id'][0])]
    #         if res['property_payment_term']:
    #             _val.update({'customer_payment_term': res['property_payment_term'][0]})
    #             _domain['customer_payment_term'] = [('id','=',res['property_payment_term'][0])]
    #     return {'value': _val,'domain':_domain}


    @api.onchange('partner_id')
    def change_partner(self, partner_id, context=None):
        res = {}
        _val = {'project_id': None, 'customer_sales_person_id': None, 'customer_payment_term': None}
        _domain = {}
        _domain['customer_sales_person_id'] = []
        _domain['customer_payment_term'] = []
        if partner_id:
            #res = self.env['res.partner'].read(partner_id, ['user_id', 'property_payment_term'])
            res = self.env['res.partner'].search([('id','=',partner_id)])
            if res['user_id']:
                _val.update({'customer_sales_person_id': res['user_id'][0]})
                _domain['customer_sales_person_id'] = [('id', '=', res['user_id'][0])]
            # if res['property_payment_term']:
            #     _val.update({'customer_payment_term': res['property_payment_term'][0]})
            #     _domain['customer_payment_term'] = [('id', '=', res['property_payment_term'][0])]
        return {'value': _val, 'domain': _domain}

    # def change_project(self,cr,uid,ids,project_id,context=None):
    #     _val = {'sales_person_id':None}
    #     _domain = {}
    #     _domain['sales_person_id'] = []
    #     if project_id:
    #         res = self.pool.get('project.project').read(cr, uid, project_id, ['sales_person_id'], context=context)
    #         if res['sales_person_id']:
    #             _val.update({'sales_person_id': res['sales_person_id'][0]})
    #             _domain['sales_person_id'] = [('id','=',res['sales_person_id'][0])]
    #     return {'value': _val, 'domain': _domain}


    @api.onchange('project_id')
    def change_project(self, project_id, context=None):
        _val = {'sales_person_id': None}
        _domain = {}
        _domain['sales_person_id'] = []
        if project_id:
            res = self.env['project.project'].search([('id','=',project_id)])
            if res['sales_person_id']:
                _val.update({'sales_person_id': res['sales_person_id'][0]})
                _domain['sales_person_id'] = [('id', '=', res['sales_person_id'][0])]
        return {'value': _val, 'domain': _domain}

Task()

class ProjectTaskWork(models.Model):
    _name = 'project.task.work'
    _description = 'Project Task Work'

    name =  fields.Char('Work summary', size=128)
    date = fields.Datetime('Date', select="1")
    task_id = fields.Many2one('project.task', 'Task', ondelete='cascade', required=True, select="1")
    hours = fields.Float('Time Spent')
    user_id = fields.Many2one('res.users', 'Done by', required=True, select="1")
    company_id = fields.Many2one('res.company',string='Company',store=True)

    reminder_date = fields.Date('Reminder Date', required=True)
    payment_note = fields.Text("Customer Promise")
    assign_to = fields.Many2one('res.users', string="Assign User")
    reminder_email = fields.Boolean('Remind by EMail', Default=False)
    state = fields.Selection([('pending', 'Pending'), ('done', 'Completed')], string="Status", default='pending')
    expected_amount = fields.Float("Expected Amount", digits=(10, 2))  # To calculate expected amount from customer as per the promise
    expected_date = fields.Date("Expected Date")  # To calculate expected payment date from customer as per the promise which will help to calculate total expected receivables for a period.

    @api.onchange('rem_date')
    def onchange_reminder_date(self, rem_date, context=None):
        if rem_date:
            return {'value': {'expected_date': rem_date}}

    def set_reminder(self, context=None):
        for r in self.browse():
            _msg = """<p> Reminder Created </p>
                  <p>
                  <li>Action: %s</li>
                   <li>Assign to: %s</li>
                   <li>Reminder Date: %s</li>
                   </p> """ % (r.name, r.assign_to.name, r.reminder_date)
            _message_id = self.env['project.task'].message_post([r.task_id], _msg)
            _notify_msg = {'message_id': _message_id, 'starred': True, 'read': False}
            _user_to_notify = []
            if r.assign_to:
                _user_to_notify.append(r.assign_to.partner_id.id)
            for f in r.task_id.message_follower_ids:
                _user_to_notify.append(f.id)
            if _user_to_notify:
                for u in set(_user_to_notify):
                    _notify_msg.update({'partner_id': u})
                    self.env('mail.notification').create(_notify_msg)
        return True

    @api.multi
    def set_done(self):
        res = self.write({'state': 'done'})
        _task_obj = self.env['project.task']
        for r in self.browse():
            _msg = """<p> Reminder task completed </p>
               <p>
               <li>Action: %s</li>
                <li>Done By: %s</li>
                <li>Payment Note: %s</li>
                </p> """ % (r.name, r.user_id.name, r.payment_note)
            _task_obj.message_post([r.task_id], _msg)
        print res
        return res

    @api.multi
    def send_reminder(self, ids=None, context=None):
        ir_model_data = self.pool.get('ir.model.data')
        template_obj = self.pool.get('email.template')
        template_id = \
        ir_model_data.get_object_reference('cic_payment_followup', 'email_template_task_reminder')[1]
        if template_id:
            _user_ids = self.read_group([('state', '=', 'pending'), ('reminder_date', '<=', datetime.date.today())],
                                        ['assign_to'], ['assign_to'])
            print 'Groups:', _user_ids
            for u in _user_ids:
                print 'Assignto :', u['assign_to']
                if u['assign_to']:
                    _rem_ids = self.search([('state', '=', 'pending'), ('reminder_date', '<=', datetime.date.today()),
                                            ('assign_to', '=', u['assign_to'][0])])
                    print 'Reminders', _rem_ids
                    # mail_id = template_obj.send_mail(cr,uid,template_id,_rem_ids[0],True)
                    self.get_reminders(u['assign_to'][0], context=context)
                    # print "Mail Send " , mail_id
        return True

    @api.multi
    def get_reminders(self, user_id, context=None):
        reminder_table = ''
        _rem_ids = self.search([('state', '=', 'pending'), ('reminder_date', '<=', datetime.date.today()),
                                         ('assign_to', '=', user_id)])
        print 'Render :', _rem_ids
        reminder_table += '''
                      <table border="2" width=100%%>
                      <tr>
                      <td>''' + _("Partner") + '''</td>
                      <td>''' + _("Project") + '''</td>
                      <td>''' + _("Task") + '''</td>
                      <td>''' + _("Reminder") + '''</td>
                      <td>''' + _("Date") + '''</td>
                      <td>''' + _("Expected Amount") + '''</td>
                      <td>''' + _("Customer Promise.") + '''</td>
                      <td>''' + _("Status.") + '''</td>
                      </tr>
                      '''
        strbegin = "<TD>"
        strend = "</TD>"
        for rem in self.browse(_rem_ids):
            row = "<TR>" + strbegin + str(rem.task_id.partner_id.name).replace("'", "\'") + strend + strbegin + str(
                rem.task_id.project_id.name).replace("'", "\'") + strend + strbegin + rem.task_id.name.replace("'",
                                                                                                               "\'") + strend + strbegin + rem.name or '' + strend + strbegin + str(
                rem.reminder_date) + strend + strbegin + str(rem.expected_amount) + strend + strbegin + "<br />".join(
                str(rem.payment_note).split("\n")) + strend + strbegin + rem.state + strend + "</TR>"
            reminder_table += row
        reminder_table += '''<tr> </tr>
                                  </table>'''
        return reminder_table

ProjectTaskWork()


# Old class """"


# class ProjectWork(models.Model):
#     #_inherit = "project.task.work"
#     _inherit = "project.task"
#
#     # _columns = {
#     #     'reminder_date':fields.date('Reminder Date',required=True),
#     #     'payment_note': fields.text("Customer Promise"),
#     #     'assign_to':fields.many2one('res.users',string="Assign User"),
#     #     'reminder_email': fields.boolean('Remind by EMail'),
#     #     'state': fields.selection([('pending','Pending'),('done','Completed')],string="Status"),
#     #     'expected_amount': fields.float("Expected Amount",digits=(10,2)), # To calculate expected amount from customer as per the promise
#     #     'expected_date': fields.date("Expected Date"), # To calculate expected payment date from customer as per the promise which will help to calculate total expected receivables for a period.
#     # }
#
#     reminder_date = fields.Date('Reminder Date', required=True)
#     payment_note  = fields.Text("Customer Promise")
#     assign_to = fields.Many2one('res.users',string="Assign User")
#     reminder_email =  fields.Boolean('Remind by EMail', Default=False)
#     state = fields.Selection([('pending','Pending'),('done','Completed')],string="Status",Default='pending')
#     expected_amount = fields.Float("Expected Amount",digits=(10,2)) # To calculate expected amount from customer as per the promise
#     expected_date =  fields.Date("Expected Date") # To calculate expected payment date from customer as per the promise which will help to calculate total expected receivables for a period.
#
#
#
#     # def onchange_reminder_date(self,cr,uid,ids,rem_date,context=None):
#     #     if rem_date:
#     #         return {'value': {'expected_date': rem_date}}
#
#     def onchange_reminder_date(self, rem_date, context=None):
#         if rem_date:
#             return {'value': {'expected_date': rem_date}}
#
#
#     # def set_reminder(self, cr, uid, ids,context=None):
#     #     for r in self.browse(cr, uid, ids):
#     #         _msg = """<p> Reminder Created </p>
#     #         <p>
#     #         <li>Action: %s</li>
#     #          <li>Assign to: %s</li>
#     #          <li>Reminder Date: %s</li>
#     #          </p> """ % (r.name,r.assign_to.name,r.reminder_date)
#     #         _message_id = self.pool.get('project.task').message_post(cr,uid,[r.task_id],_msg)
#     #         _notify_msg = {'message_id':_message_id,'starred':True,'read':False}
#     #         _user_to_notify =[]
#     #         if r.assign_to:
#     #             _user_to_notify.append(r.assign_to.partner_id.id)
#     #         for f in r.task_id.message_follower_ids:
#     #             _user_to_notify.append(f.id)
#     #         if _user_to_notify:
#     #             for u in set(_user_to_notify):
#     #                 _notify_msg.update({'partner_id': u})
#     #                 self.pool.get('mail.notification').create(cr,uid,_notify_msg)
#     #     return True
#
#     def set_reminder(self, context=None):
#         for r in self.browse():
#             _msg = """<p> Reminder Created </p>
#                <p>
#                <li>Action: %s</li>
#                 <li>Assign to: %s</li>
#                 <li>Reminder Date: %s</li>
#                 </p> """ % (r.name, r.assign_to.name, r.reminder_date)
#             _message_id = self.env['project.task'].message_post([r.task_id], _msg)
#             _notify_msg = {'message_id': _message_id, 'starred': True, 'read': False}
#             _user_to_notify = []
#             if r.assign_to:
#                 _user_to_notify.append(r.assign_to.partner_id.id)
#             for f in r.task_id.message_follower_ids:
#                 _user_to_notify.append(f.id)
#             if _user_to_notify:
#                 for u in set(_user_to_notify):
#                     _notify_msg.update({'partner_id': u})
#                     self.env('mail.notification').create(_notify_msg)
#         return True
#
#     # def set_done(self,cr,uid,ids,context=None):
#     #     res = self.write(cr, uid, ids,{'state':'done'},context=context)
#     #     _task_obj = self.pool.get('project.task')
#     #     for r in self.browse(cr,uid,ids):
#     #         _msg = """<p> Reminder task completed </p>
#     #         <p>
#     #         <li>Action: %s</li>
#     #          <li>Done By: %s</li>
#     #          <li>Payment Note: %s</li>
#     #          </p> """ % (r.name,r.user_id.name,r.payment_note)
#     #         _task_obj.message_post(cr,uid,[r.task_id],_msg)
#     #     return res
#
#
#     def set_done(self,context=None):
#         res = self.write({'state':'done'},context=context)
#         _task_obj = self.env['project.task']
#         for r in self.browse():
#             _msg = """<p> Reminder task completed </p>
#             <p>
#             <li>Action: %s</li>
#              <li>Done By: %s</li>
#              <li>Payment Note: %s</li>
#              </p> """ % (r.name,r.user_id.name,r.payment_note)
#             _task_obj.message_post([r.task_id],_msg)
#         return res
#
#     # def send_reminder(self,cr,uid,ids=None,context=None):
#     #     ir_model_data = self.pool.get('ir.model.data')
#     #     template_obj = self.pool.get('email.template')
#     #     template_id = ir_model_data.get_object_reference(cr, uid, 'cic_payment_followup', 'email_template_task_reminder')[1]
#     #     if template_id:
#     #         _user_ids = self.read_group(cr,uid,[('state','=','pending'), ('reminder_date','<=', datetime.date.today())], ['assign_to'],['assign_to'])
#     #         print 'Groups:',  _user_ids
#     #         for u in _user_ids:
#     #             print 'Assignto :', u['assign_to']
#     #             if u['assign_to']:
#     #                 _rem_ids = self.search(cr,uid,[('state','=','pending'), ('reminder_date','<=', datetime.date.today()),('assign_to','=',u['assign_to'][0])])
#     #                 print 'Reminders' , _rem_ids
#     #                 # mail_id = template_obj.send_mail(cr,uid,template_id,_rem_ids[0],True)
#     #                 self.get_reminders(cr, uid, ids, u['assign_to'][0], context=context)
#     #                 # print "Mail Send " , mail_id
#     #     return True
#
#     def send_reminder(self, ids=None, context=None):
#         ir_model_data = self.pool.get('ir.model.data')
#         template_obj = self.pool.get('email.template')
#         template_id = \
#         ir_model_data.get_object_reference('cic_payment_followup', 'email_template_task_reminder')[1]
#         if template_id:
#             _user_ids = self.read_group([('state', '=', 'pending'), ('reminder_date', '<=', datetime.date.today())],
#                                         ['assign_to'], ['assign_to'])
#             print 'Groups:', _user_ids
#             for u in _user_ids:
#                 print 'Assignto :', u['assign_to']
#                 if u['assign_to']:
#                     _rem_ids = self.search([('state', '=', 'pending'), ('reminder_date', '<=', datetime.date.today()),
#                                             ('assign_to', '=', u['assign_to'][0])])
#                     print 'Reminders', _rem_ids
#                     # mail_id = template_obj.send_mail(cr,uid,template_id,_rem_ids[0],True)
#                     self.get_reminders(u['assign_to'][0], context=context)
#                     # print "Mail Send " , mail_id
#         return True
#
#     # def get_reminders(self,cr,uid,ids,user_id,context=None):
#     #     reminder_table = ''
#     #     _rem_ids = self.search(cr,uid,[('state','=','pending'), ('reminder_date','<=', datetime.date.today()),('assign_to','=',user_id)])
#     #     print 'Render :',_rem_ids
#     #     reminder_table += '''
#     #                 <table border="2" width=100%%>
#     #                 <tr>
#     #                 <td>''' + _("Partner") + '''</td>
#     #                 <td>''' + _("Project") + '''</td>
#     #                 <td>''' + _("Task") + '''</td>
#     #                 <td>''' + _("Reminder") + '''</td>
#     #                 <td>''' + _("Date") + '''</td>
#     #                 <td>''' + _("Expected Amount") + '''</td>
#     #                 <td>''' + _("Customer Promise.") + '''</td>
#     #                 <td>''' + _("Status.") + '''</td>
#     #                 </tr>
#     #                 '''
#     #     strbegin = "<TD>"
#     #     strend = "</TD>"
#     #     for rem in self.browse(cr,uid,_rem_ids):
#     #         row = "<TR>" + strbegin + str(rem.task_id.partner_id.name).replace("'","\'") + strend + strbegin + str(rem.task_id.project_id.name).replace("'","\'") + strend + strbegin+ rem.task_id.name.replace("'","\'") + strend + strbegin + rem.name or '' + strend + strbegin + str(rem.reminder_date) + strend + strbegin + str(rem.expected_amount) + strend + strbegin + "<br />".join(str(rem.payment_note).split("\n")) + strend + strbegin + rem.state + strend + "</TR>"
#     #         reminder_table += row
#     #     reminder_table +='''<tr> </tr>
#     #                             </table>'''
#     #     return reminder_table
#
#     def get_reminders(self, user_id, context=None):
#         reminder_table = ''
#         _rem_ids = self.search([('state', '=', 'pending'), ('reminder_date', '<=', datetime.date.today()),
#                                          ('assign_to', '=', user_id)])
#         print 'Render :', _rem_ids
#         reminder_table += '''
#                       <table border="2" width=100%%>
#                       <tr>
#                       <td>''' + _("Partner") + '''</td>
#                       <td>''' + _("Project") + '''</td>
#                       <td>''' + _("Task") + '''</td>
#                       <td>''' + _("Reminder") + '''</td>
#                       <td>''' + _("Date") + '''</td>
#                       <td>''' + _("Expected Amount") + '''</td>
#                       <td>''' + _("Customer Promise.") + '''</td>
#                       <td>''' + _("Status.") + '''</td>
#                       </tr>
#                       '''
#         strbegin = "<TD>"
#         strend = "</TD>"
#         for rem in self.browse(_rem_ids):
#             row = "<TR>" + strbegin + str(rem.task_id.partner_id.name).replace("'", "\'") + strend + strbegin + str(
#                 rem.task_id.project_id.name).replace("'", "\'") + strend + strbegin + rem.task_id.name.replace("'",
#                                                                                                                "\'") + strend + strbegin + rem.name or '' + strend + strbegin + str(
#                 rem.reminder_date) + strend + strbegin + str(rem.expected_amount) + strend + strbegin + "<br />".join(
#                 str(rem.payment_note).split("\n")) + strend + strbegin + rem.state + strend + "</TR>"
#             reminder_table += row
#         reminder_table += '''<tr> </tr>
#                                   </table>'''
#         return reminder_table
#
#
# ProjectWork()


class Project(models.Model):
    _inherit = 'project.project'

    # _columns = {
    #     'project_company_id':fields.many2one('res.company',"Company(Database)",required=True, help= "Company Where Project Registered"),
    #     'contact_ids': fields.many2many('res.partner','project_contact_rel','project_id','contact_id',string="Contacts",domain=[('is_company','=',False)])
    #     #Company Where Project Registered,existing company_id will be registered as per logged in user default company
    #     #project_company_id used to filter projects and checks received
    # }

    project_company_id = fields.Many2one('res.company', "Company(Database)", required=True,
                                         help="Company Where Project Registered")
    contact_ids = fields.Many2many('res.partner', 'project_contact_rel', 'project_id', 'contact_id', string="Contacts",
                                   domain=[('is_company', '=', False)])


Project()

class ResPartner(models.Model):
    _inherit = "res.partner"

    # _columns = {
    #     'project_ids' : fields.one2many('project.project','partner_id',string="Projects"),
    # }

    project_ids = fields.One2many('project.project', 'partner_id', string="Projects")

ResPartner()





