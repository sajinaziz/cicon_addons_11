from odoo import models, fields,api


class CiconSaleConditionTemplate(models.Model):
    _name = 'cicon.sale.condition.template'
    _description = "CICON Sale Condition Template"

    name = fields.Char('Heading', required=True)
    condition_ids = fields.One2many('cicon.sale.condition', 'template_id', string="Conditions")

    _sql_constraints = [('uniq_templ', 'UNIQUE(name)', 'Template name should be unique !')]


class CiconSaleCondition(models.Model):
    _name = 'cicon.sale.condition'
    _description = "CICON Sale Condition"

    template_id = fields.Many2one('cicon.sale.condition.template', ondelete='cascade', string='Template')
    sequence = fields.Integer('Sequence')
    name = fields.Char('Condition', required=True)
    description = fields.Html('Description', required=True)

    _sql_constraints = [('uniq_cond', 'UNIQUE(template_id,name)', 'Template name should be unique !')]


class SaleOrder(models.Model):
    _inherit = "sale.order"

    cicon_template_id = fields.Many2one('cicon.sale.condition.template', string="Quotation Template")