from odoo import models, fields, api

class ResPartner(models.Model):
    _inherit = "res.partner"

    # _columns = {
    #     'sun_account_id': fields.many2one('cic.sun.account','Sun Account Number'),
    #     'interest_rate_od': fields.float('Interest Rate for Over Due Amount', help="Interest Rate for Payment over due"),
    #     'sun_account_ids': fields.one2many('cic.sun.account' ,'partner_id','Sun Accounts'),
    #     'interest_rate_od': fields.float('Interest Rate for OD', help="Interest Rate for Payment over due"),
    # }
    # _sql_constraints = [
    #     ('sun_no_uniq', 'UNIQUE(sun_account_id)', 'Sun Account Number must be unique!'),]

    interest_rate_od = fields.Float('Interest Rate for Over Due Amount', help="Interest Rate for Payment over due")
    sun_account_ids = fields.One2many('cic.sun.account', 'partner_id', 'Sun Accounts')

    # def name_get(self, cr, uid, ids, context=None):
    #     if context is None:
    #         context = {}
    #     if isinstance(ids, (int, long)):
    #         ids = [ids]
    #     res = []
    #     for record in self.browse(cr, uid, ids, context=context):
    #
    #         name = record.name
    #         # if record.parent_id and not record.is_company:
    #         #     name =  "%s, %s" % (record.parent_id.name, name)
    #         if context.get('show_address'):
    #             name = name + "\n" + self._display_address(cr, uid, record, without_company=True, context=context)
    #             name = name.replace('\n\n','\n')
    #             name = name.replace('\n\n','\n')
    #         if context.get('show_email') and record.email:
    #             name = "%s <%s>" % (name, record.email)
    #         res.append((record.id, name))
    #     return res
    #

    def name_get(self, context=None):
        if context is None:
            context = {}
        # if isinstance(ids, (int, long)):
        #     ids = [ids]
        res = []
        for record in self:
            name = record.name
            # if record.parent_id and not record.is_company:
            #     name =  "%s, %s" % (record.parent_id.name, name)
            if context.get('show_address'):
                name = name + "\n" + self._display_address(record, without_company=True, context=context)
                name = name.replace('\n\n','\n')
                name = name.replace('\n\n','\n')
            if context.get('show_email') and record.email:
                name = "%s <%s>" % (name, record.email)
            res.append((record.id, name))
            #print res
        return res


ResPartner()


class Project(models.Model):
    _inherit = 'project.project'
    # _columns = {
    #     'sun_account_ids': fields.one2many('cic.sun.account','project_id','Sun Account Number'),
    #     'sales_person_id': fields.many2one('res.users', "Sales person"),
    #     'project_payment_term_id': fields.many2one('account.payment.term', 'Project Payment Terms'),
    #     'project_credit_limit': fields.float('Project Credit Limit')
    #     #Sun System Account For Project
    # }

    sun_account_ids = fields.One2many('cic.sun.account', 'project_id', 'Sun Account Number')
    sales_person_id = fields.Many2one('res.users', "Sales person")
    project_payment_term_id = fields.Many2one('account.payment.term', 'Project Payment Terms')
    project_credit_limit = fields.Float('Project Credit Limit')



    # def onchange_partner_id(self, cr, uid, ids, part=False, context=None):
    #     _res = super(Project,self).onchange_partner_id(cr, uid, ids, part=part, context=context)
    #     if part:
    #         _partner = self.pool.get('res.partner').read(cr,uid,part,['user_id'])
    #         if _partner['user_id']:
    #             _res.update({'sales_person_id':_partner['user_id'][0]})
    #     return {'value': _res}

    # def onchange_partner_id(self, ids, part=False, context=None):
    #     _res = super(Project, self).onchange_partner_id(ids, part=part, context=context)
    #     if part:
    #         _partner = self.env['res.partner'].read(part, ['user_id'])
    #         if _partner['user_id']:
    #             _res.update({'sales_person_id': _partner['user_id'][0]})
    #     return {'value': _res}


            # _sql_constraints = [
    #     ('sun_no_uniq', 'UNIQUE(sun_account_id)', 'Sun Account Number must be unique!'),]

Project()


class CicSunDb(models.Model):
    _name = 'cic.sun.db'
    _description = 'Sun Account DB'

    # _columns = {
    #     'db_name': fields.char('DB Name', size=10 , required=True),
    #     'db_code': fields.char('DB Code', size=10, required=True),
    # }

    db_name = fields.Char('DB Name', size=10, required=True)
    db_code = fields.Char('DB Code', size=10, required=True)

    _sql_constraints = [
        ('db_code_uniq', 'UNIQUE(db_code)', 'Sun DB must be unique!'),
        ('db_name_uniq', 'UNIQUE(db_name)', 'Sun DB must be unique!')]

CicSunDb()


class CicSunAccount(models.Model):
    _name = 'cic.sun.account'
    _description = "Sun System Account Numbers"
    _rec_name = "sun_account_no"

    # def _get_db_selection(self,cr,uid,context=None):
    #     sun_db_ids = self.pool.get('cic.sun.db').search(cr,uid,[])
    #     sun_db = self.pool.get('cic.sun.db').read(cr,uid,sun_db_ids,['db_name','db_code'])
    #     res = []
    #     for x in sun_db:
    #         res.append((x['db_code'],x['db_name']))
    #     return res

    def _get_db_selection(self, context=None):
        sun_db_ids = self.env['cic.sun.db'].search([])
        res = []
        for x in sun_db_ids:
            res.append((x.db_code, x.db_name))
        #print res
        return res

    # _columns = {
    #     'sun_db':fields.selection(selection=_get_db_selection ,string='SUN DB',required=True),
    #     'sun_account_no': fields.char('Sun Account Number', size=10, help="Sun System Account Number", required=True),
    #     'partner_id': fields.many2one('res.partner',string='Customer',required=True),
    #     'project_id': fields.many2one('project.project',string="Project",domain="[('partner_id','=',partner_id)]")
    #
    # }

    sun_db = fields.Selection(selection=_get_db_selection, string='SUN DB', required=True)
    sun_account_no = fields.Char('Sun Account Number', size=10, help="Sun System Account Number", required=True)
    partner_id = fields.Many2one('res.partner', string='Customer', required=True)
    project_id = fields.Many2one('project.project', string="Project", domain="[('partner_id','=',partner_id)]")

    _sql_constraints = [
        ('acc_no_uniq', 'UNIQUE(sun_db,sun_account_no)', 'Sun Account Number must be unique!'),]

    def getSelectionValue(self,fieldName, field_val):
        return dict(self.fields_get()[fieldName]['selection'])[field_val]

    # def name_get(self, cr, uid, ids, context=None):
    #     res = []
    #     for r in self.read(cr, uid, ids,  ['sun_db', 'sun_account_no'], context):
    #         if r['sun_db']:
    #             res.append((r['id'], self.getSelectionValue(cr,uid,'sun_db', r['sun_db']) + ' / ' + r['sun_account_no']))
    #         else:
    #             res.append((r['id'], ' ' + ' / ' + r['sun_account_no']))
    #     return res

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            if record.sun_db and record.sun_account_no:
                if record.sun_db:
                    result.append((record.id, self.getSelectionValue('sun_db',record.sun_db) + '/' + record.sun_account_no))
                else:
                    result.append((record.id, record.sun_account_no))
        return result
    #
    # @api.model
    # def name_search(self, sun_db, args=None, operator='ilike', limit=100):
    #     args = args or []
    #     recs = self.browse()
    #     if sun_db:
    #         recs = self.search([('sun_db', '=', sun_db)] + args, limit=limit)
    #     if not recs:
    #         recs = self.search([('sun_db', operator, sun_db)] + args, limit=limit)
    #     return recs.name_get()


    def validate_partner(self, ids, sun_account=None):
        return False

    # Save From Wizard required this Function

    @api.multi
    def add_sun_account(self, ids, context=None):
        return ids

CicSunAccount()
