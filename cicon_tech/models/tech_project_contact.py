from odoo import models, fields, api


class ProjectContact(models.Model):
    """Job Site Contact information to address (Attn)  on Submittal Form"""
    _name = 'tech.project.contact'
    _description = "Contact Details"
    # _log_access = False
    _rec_name = 'display_name'

    @api.one
    @api.depends('name', 'salutation')
    def _compute_display_name(self):
        """To show Name with Salutation on field 'display_name'"""
        self.display_name = (self.salutation or '') + ' ' + unicode(self.name)

    display_name = fields.Char(string='Name', compute=_compute_display_name, store=False)
    name = fields.Char('Name', size=250, required=True, help="Contact Full Name")
    job_site_id = fields.Many2one('cicon.job.site', 'Job Site Name', required=True, ondelete='cascade')
    # TODO:Change with contact Title or  resPartner Contact
    salutation = fields.Char('Salutation', size=10)
    #title_id = fields.Many2one('res.partner.title', string="Title")
    designation = fields.Char('Designation', size=150)
    email = fields.Char('Email', size=250, help="Contact Valid Email ID")

ProjectContact()
