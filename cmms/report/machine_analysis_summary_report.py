from openerp import fields,models,api
from dateutil import rrule
from datetime import date

_machines = None
_inv_lines = None


class ReportMachineAnalysisSummary(models.AbstractModel): # Report File Name
    _name = 'report.cmms.report_machine_analysis_summary_template'

    @api.multi
    def render_html(self, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('cmms.report_machine_analysis_summary_template')
        _docs = self._get_report_data()



        docargs = {
            'doc_model': report.model,
            'docs': _docs,
            'heading': self._context.get('heading'),
            'year' : self._context.get('year'),
            'get_category': self._get_categories,
            'get_machine': self._get_machines,
            'get_breakdown_count': self._job_order_count
        }

        return report_obj.render('cmms.report_machine_analysis_summary_template', docargs)

    def _get_report_data(self):
        _qry =[]
        if self._context.get('company_id'):
            _qry.append(('company_id','=',self._context.get('company_id')))
        if self._context.get('machine_categ_ids'):
            _qry.append(('category_id', 'in', self._context.get('machine_categ_ids')))
        self._machines = self.env['cmms.machine'].search(_qry)
        _types = self._machines.mapped('type_id').sorted(lambda t:t.name)
        return _types

    def _job_order_count(self, _mid):
        year = self._context.get('year')
        _start_date = self._context.get('from_date')
        _end_date = self._context.get('to_date')

        breakdown_list = []
        _breakdown_entry = {}
        _res = self.env['cmms.job.order'].read_group(domain=[('job_order_date', '>=',_start_date),('job_order_date', '<=', _end_date),('machine_id', '=', _mid),('job_order_type','=','breakdown')],
                                                     fields=['job_order_date','job_order_type'], groupby=[('job_order_date:month'),('job_order_type')])
        for r in _res:
            _breakdown_entry[r['job_order_date:month'].replace(year,'').strip()] = r['job_order_date_count']
        _total_jobOrder = sum(_breakdown_entry.values())
        if _total_jobOrder > 0:
            _breakdown_entry['total_job_order'] = _total_jobOrder
        else:
            _breakdown_entry['total_job_order'] = ''
        breakdown_list.append(_breakdown_entry)
        #print breakdown_list
        return breakdown_list


    def _get_categories(self, _type):
        _categs = self._machines.filtered(lambda r: r.type_id == _type).mapped('category_id').sorted(lambda c: c.name)
        return _categs

    def _get_machines(self, _type, _categ):
        year = self._context.get('year')
        _start_date = self._context.get('from_date')
        _end_date = self._context.get('to_date')
        _machine_list = []
        _machines = self._machines.filtered(lambda r: r.category_id == _categ and r.type_id == _type)

        for _mac in _machines.sorted(lambda a:a.code):
            _machine_entry = {}
            month_wise = self.env['cmms.store.invoice.line'].read_group(domain=[('invoice_date', '>=',_start_date),('invoice_date', '<=', _end_date),('machine_id', '=',_mac.id)],
                                                                                fields=['invoice_date','machine_id','amount'],
                                                                                groupby=[('invoice_date:month'),('machine_id')])
            #print month_wise
            for _res in month_wise:
                _machine_entry[_res['invoice_date:month'].replace(year,'').strip()] = round(_res['amount'],2)
            _total_expense = sum(_machine_entry.values())
            if _total_expense > 0:
                _machine_entry['total_expense'] = "%.2f" % round(_total_expense, 2)
            else:
                _machine_entry['total_expense'] = ''
            _machine_entry.update(machine_id=_mac)
            _machine_list.append(_machine_entry)
        return _machine_list
