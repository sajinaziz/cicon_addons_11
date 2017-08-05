from odoo import models, api, fields

_inv_lines = None


class MaterialApprovalReport(models.AbstractModel): # Report File Name
    _name = 'report.cicon_qc.qc_material_approval_report_template'

    @api.model
    def render_html(self, docids, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('cicon_qc.qc_material_approval_report_template')
        _docs = self.env['cicon.job.site'].search([('id', 'in', docids)])
        docargs = {
             'doc_ids': docids,
             'doc_model': report.model,
             'docs': _docs,
             'get_origins': self._get_origins,
             'get_approval': self._get_material_approved_project,
             'get_state_list': self._get_state_list,
             'get_datetime': self._get_current_datetime
        }
        return report_obj.render('cicon_qc.qc_material_approval_report_template', docargs)

    def _get_state_list(self):
        return dict(self.env['qc.material.approval'].fields_get(allfields=['state'])['state']['selection'])

    def _get_origins(self):
        _steel_origins = self.env['product.attribute.value'].search([('attribute_id.name','=','Steel Origin')])
        return _steel_origins

    def _get_material_approved_project(self, _site_id):
        _approved_list = self.env['qc.material.approval'].search([('job_site_id','=', _site_id)])
        _res = {}
        for _app in _approved_list:
            _res[_app.origin_attrib_value_id.id] = _app.state
        return _res

    def _get_current_datetime(self):
        return self.env['cicon.customer.order'].get_datetime_current()

