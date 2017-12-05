from odoo import models,fields, api


class CiconCustomerBusinessType(models.Model):
    _name = 'cicon.customer.business.type'

    name = fields.Char('Company Type', required=True)

    _sql_constraints = [('unique_btype', 'UNIQUE(name)', 'Business Type should be Unique !')]


class CiconCustomerLicenseType(models.Model):
    _name = 'cicon.customer.license.type'

    name = fields.Char('License Type', required=True)

    _sql_constraints = [('unique_lictype', 'UNIQUE(name)', 'License Type should be Unique !')]


class CiconCustomerContactType(models.Model):
    _name = 'cicon.customer.contact.type'

    name = fields.Char('Contact Type', required=True)

    _sql_constraints = [('unique_ctype', 'UNIQUE(name)', 'Contact Type should be Unique !')]


class ResPartner(models.Model):
    _inherit = 'res.partner'

    credit_application_ids = fields.One2many('cicon.customer.credit.application', 'partner_id',  groups="cicon_credit.group_cicon_credit_user", string="Credit Applications")
    contact_type_ids = fields.Many2many('cicon.customer.contact.type', 'partner_contact_type_rel', 'partner_id', 'contact_type_id', groups="cicon_credit.group_cicon_credit_user", string="Contact Type" )
    passport_no = fields.Char('Passport No.')


class CiconCustomerCreditApplication(models.Model):
    _name = "cicon.customer.credit.application"
    _description = "Customer Credit Application"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char("Ref#", required=True)

    partner_id = fields.Many2one('res.partner', string="Customer", required=True,track_visibility='onchange')
    year_establish = fields.Char('Year Established',track_visibility='onchange')
    industry_id = fields.Many2one('res.partner.industry',related='partner_id.industry_id', string='Nature of Business', readonly=True)
    business_type_id = fields.Many2one('cicon.customer.business.type', string="Company Type",track_visibility='onchange')
    license_type_id = fields.Many2one('cicon.customer.license.type', string='Trade License Type',track_visibility='onchange')
    license_validity = fields.Date('Valid up to',track_visibility='onchange')
    paid_capital = fields.Float('Paid Up Capital',track_visibility='onchange')
    contact_ids = fields.One2many('res.partner', related='partner_id.child_ids', string="Contacts", readonly=True)
    partner_bank_ids = fields.One2many('res.partner.bank', related='partner_id.bank_ids', string="Banks", readonly=True)

    approx_business = fields.Float('Anticipated Monthly Business',track_visibility='onchange')
    credit_days_req = fields.Integer('Credit Period Required',track_visibility='onchange')
    credit_limit_req = fields.Float('Credit Limit Required',track_visibility='onchange')

    product_temp_ids = fields.Many2many(comodel_name='product.template', relation='cicon_credit_app_product_temp_rel', column1='credit_app_id', column2= 'product_temp_id', string="Products Required")
    partner_document_ids = fields.One2many('cicon.document', related='partner_id.document_ids', string="Documents", readonly=True)

    state = fields.Selection([('new', 'Draft'), ('pending', 'Submitted'), ('approved', 'Approved'),
                              ('reject', 'Rejected'), ('cancel', 'Cancelled')], string='State', default='new', track_visibility='onchange')








