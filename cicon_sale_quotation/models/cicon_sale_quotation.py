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


class CiconSaleOrderCondition(models.Model):
    _name = 'cicon.sale.order.condition'
    _description = "Sale Order Condition"

    sale_order_id = fields.Many2one('sale.order', string="Sale Order")
    description = fields.Html('Description')


class SaleOrder(models.Model):
    _inherit = "sale.order"

    cicon_template_ids = fields.Many2many('cicon.sale.condition.template', 'cicon_sale_cond_temp_rel', 'sale_order_id', 'templ_id', string="Quotation Template")
    sale_condition_ids = fields.One2many('cicon.sale.order.condition','sale_order_id', string="Sale Condition")

    @api.onchange('cicon_template_ids')
    def _on_change_temp(self):
        _res = []
        for _tmpl in self.cicon_template_ids:
            for _cond in _tmpl.condition_ids:
                _res.append({'description': _cond.description})
        self.sale_condition_ids = _res
