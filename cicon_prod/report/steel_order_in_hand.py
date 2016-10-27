import time

from odoo.report import report_sxw
from odoo.osv import osv
from odoo import models, api
from datetime import date,datetime

#
# class CiconOrderInHand(report_sxw.rml_parse):
#     def __init__(self, cr, uid, name, context=None):
#         print context
#         super(CiconOrderInHand, self).__init__(cr, uid, name, context=context)
#         self.localcontext.update({
#             'time': time,
#         })
#         self.context = context


class cicon_steel_order_in_hand(models.AbstractModel): # Report File Name
    _name = 'report.cicon_prod.cicon_steel_order_in_hand_template'
    # _inherit = 'report.abstract_report'
    # _template = 'cicon_prod.cicon_steel_order_in_hand_template'
    # _wrapped_report_class = CiconOrderInHand

    @api.multi
    def render_html(self,docids,data=None):
        data = data if data is not None else {}
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('cicon_prod.cicon_steel_order_in_hand_template')
        rml = report_sxw.rml_parse(self._cr, self._uid, 'cicon_steel_order_in_hand_template')
        docargs = {
            'doc_ids': data.get('ids'),
            'doc_model': report.model,
            'docs': self.get_docs(data.get('ids')),
            'formatLang': rml.formatLang,
            'digit': self._context.get('digits', 0),
            'heading': self._context.get('report_heading', ''),
        }
        return report_obj.render('cicon_prod.cicon_steel_order_in_hand_template', docargs)

    def get_docs(self, ids):
        _records = self.env['cicon.order.analysis.report'].browse(ids)
        #Create a tuple project with distinct records , sorted by name customer name then project name
        _projects = sorted(list(set([(r.partner_id, r.project_id) for r in _records])), key=lambda c: (c[0].name, c[1].name))
        #Create a dictionary with partner and project record
        _customer_project_list = [dict(partner_id=x[0], project_id=x[1]) for x in _projects]
        # loop the list
        for project in _customer_project_list:
            _lines = filter(lambda x: project['project_id'].id == x.project_id.id, _records) #get records for the current Project
            _qty = {}
            for _dia in set([l.dia_attrib_value_id for l in _lines]): # Loop through the distinct dia from records
                _qty[_dia.name] = sum([q.quantity for q in _lines if q.dia_attrib_value_id.id == _dia.id]) # sum and store to _dia Dictionary with the Dia Key
            project['quantity'] = _qty # Add dia to Main Dictionary
        _dia_val = []
        for i, k in enumerate(_customer_project_list):
            _dia_val.extend(k['quantity'].keys()) # get all Dia Key and add  to _dia_val List for Grand Total
        _grand_total = {}
        for dia_value in _dia_val: # Loop Dia and  sum , store to _grand_total Dictionary with the Dia Key
            _grand_total[dia_value] = sum([i['quantity'].get(dia_value, 0) for i in _customer_project_list])
        _vals = []
        _product_templates = self.env['product.template'].search([('id', 'in', self._context.get('prod_template_ids'))])
        # Cretae a list of dia used in selected templates sorted with sequence
        for t in _product_templates:
            for a in t.attribute_line_ids:
                if a.attribute_id.name in ('Diameter', 'Reduce Coupler Type'):
                    _vals.extend(a.value_ids)
        _dia_vals = sorted(list(set(_vals)), key=lambda v: v.sequence)
        _res = dict(records=_customer_project_list, grand_total=_grand_total, diameters=_dia_vals) # Assign to parent Dictionary with then three Keys.
        return _res

#
# class trip_summary_reprt(models.AbstractModel): # Report File Name
#     _name = 'report.cicon_prod.cicon_steel_trip_summary_template'
#
#     @api.multi
#     def render_html(self, data=None):
#         report_obj = self.env['report']
#         report = report_obj._get_report_from_name('cicon_prod.cicon_steel_trip_summary_template')
#         rml = report_sxw.rml_parse(self._cr, self._uid, 'cicon_steel_trip_summary_template')
#         docargs = {
#             'doc_ids': self.ids,
#             'doc_model': report.model,
#             'docs': self.env[report.model].search([('id', 'in', self._ids)]),
#             'formatLang': rml.formatLang,
#         }
#         return report_obj.render('cicon_prod.cicon_steel_trip_summary_template', docargs)