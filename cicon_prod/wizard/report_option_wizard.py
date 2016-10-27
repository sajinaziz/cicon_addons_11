from odoo import models, osv, fields, api


class cicon_prod_report_option_wizard(models.TransientModel):
    _name = 'cicon.prod.report.option.wizard'
    _description = "Production Report Options"

    partner_id = fields.Many2one('res.partner', string='Customer',domain="[('customer','=',True)]")
    project_id = fields.Many2one('cicon.job.site', string='Project', domain="[('partner_id','=',partner_id)]")
    #project_id = fields.Many2one('res.partner.project', string='Project',domain="[('partner_id','=',partner_id)]")
    template_id = fields.Many2one('cicon.prod.report.template', 'Report Name', required=True)

    @api.multi
    def show_report(self,data):
        _parms = []
        _parms.append(('state', 'not in', ['delivered', 'cancel', 'transfer']))
        if self.partner_id:
            _parms.append(('partner_id', '=', self.partner_id.id))
        if self.project_id:
            _parms.append(('project_id', '=', self.project_id.id))
        _categ_ids = [x.id for x in self.template_id.prod_categ_ids]
        _parms.append(('product_tmpl_id', 'in', _categ_ids))
        _po_ids = self.env['cicon.order.analysis.report'].search(_parms)
        _datas = {'model': 'cicon.order.analysis.report',
                  'ids': _po_ids.ids,
                  'form': {}
        }
        ctx = dict(self._context)
        ctx['prod_template_ids'] = _categ_ids
        ctx['digits'] = self.template_id.digits
        ctx['report_heading'] = self.template_id.name
        #datas = {'ids': self.env.context.get('active_ids', [])}
        return self.with_context(ctx).env['report'].get_action(self, report_name='cicon_prod.cicon_steel_order_in_hand_template', data=_datas)

cicon_prod_report_option_wizard()


class cicon_prod_report_template(models.Model):
    _name = 'cicon.prod.report.template'

    name = fields.Char('Report Option', size=32)
    report_id = fields.Many2one('ir.actions.report.xml', domain="[('model','=','cicon.order.analysis.report')]", ondelete='set null',string='Report to Show')
    prod_categ_ids = fields.Many2many('product.template', 'cic_prod_temp_rpt_rel', 'template_id','prod_template_id', string= 'Product Templates', required=True,help="Select Template for the Filter")
    digits = fields.Integer('Decimal in Report')

cicon_prod_report_template()



