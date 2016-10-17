from odoo import models, fields, api


class Submittal(models.Model):
    """Master Submittal information
    used with class : 'tech.submittal.revision' as delegation inheritance
        Please refer : Inheritance and extension Section in ODOO Documentation
    This class to keep the Master information of Submission, each new submission create new mater entry
    and there after revisions just refer to the main submittal on class 'tech.submittal.revision'
    """
    _name = 'tech.submittal'
    _description = "Technical Submittal"

    # unique Submittal Code generated from class 'tech.submittal.revision'
    name = fields.Char('Submittal Ref',  required=True, index=True)
    partner_id = fields.Many2one('res.partner', string="Customer", index=True)
    job_site_id = fields.Many2one('cicon.job.site', "Job Site Name", required=True,
                                  domain="[('partner_id','=',partner_id)]", index=True)
    site_ref_no = fields.Char(related='job_site_id.site_ref_no', string="Site Ref #", store=False, readonly=True)
    coordinator_id = fields.Many2one('res.users', related='job_site_id.coordinator_id',
                                     string="Coordinated By", store=False,  readonly=True)
    company_id = fields.Many2one('res.company', "Company", required=True,
                                 default=lambda self: self.env.user.company_id.id)
    revision_ids = fields.One2many('tech.submittal.revision', 'submittal_id', "Revisions")
    # Count on submittal just to ease the generation of Reference Code in  class 'tech.submittal.revision'
    submittal_common_count = fields.Integer('Submittal Count Global')
    # Count on submittal per job site  just to ease the generation of Reference Code in  class 'tech.submittal.revision'
    submittal_project_count = fields.Integer('Submittal Project Count')

    @api.model
    def create(self, vals):
        """
            :param: vals- values to create Submittal
            Note:
                Create need to override to block creation of submittal on new revision
                  if name already available then it should return id of existing record.
        """
        _name = vals.get('name')
        _exists = self.search([('name', '=', _name)])
        if _exists:
            res = _exists[0]
        else:
            res = super(Submittal, self).create(vals)
        return res

    _sql_constraints = [('unique_sub_ref', 'unique(name)', 'Submittal Ref Should be Unique'),
                        ('unique_sub_count_common', 'unique(submittal_common_count)',
                         'Submittal Common Count Should be Unique'),
                        ('unique_sub_count_project', 'unique(submittal_project_count,job_site_id)',
                         'Submittal Count On Project Should be Unique')]

Submittal()


class DeliveryDetails(models.Model):
    _name = "tech.delivery.details"
    _description = "Delivery Details By Submittal"
    """ Delivery information against revision """

    # TODO: To be link with Production Customer order and Delivery
    name = fields.Char('Order No', size=50, required=True)
    revision_id = fields.Many2one('tech.submittal.revision', "Submittal Revision")
    delivered_qty = fields.Float('Delivered Qty', required=True)

DeliveryDetails()
