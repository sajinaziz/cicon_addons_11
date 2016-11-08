from odoo import fields,models,api


_inv_lines = None


class ReportPartsbyProductTypeSummary(models.AbstractModel): # Report File Name
    _name = 'report.cmms.report_partsby_producttype_summary_template'

    @api.model
    def render_html(self, docids,data=None):
        data = data if data is not None else {}
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('cmms.report_partsby_producttype_summary_template')
        _docs = self._get_report_data(data.get('ids', data.get('active_ids')))

       # _get_category = self._get_categories
        docargs = {
            'doc_ids': data.get('ids', data.get('active_ids')),
            'doc_model': report.model,
            'docs': _docs,
            'heading': self._context.get('heading'),
			'rpt_option': self._context.get('report_option'),	
            'get_total': self._get_parts_total,
            'get_category': self._get_categories,
            'get_machine': self._get_machines,
            'get_invoice': self._get_invoices,
            'get_grand_total': self._get_grand_total,
            'get_machine_types': self._get_machine_types,
            'get_ptypes_for_mtype': self._get_ptypes_for_mtype ,
            'get_total_mtype_ptype': self._get_total_for_machine_type_prod_type,
            'get_total_for_machine_type': self._get_total_for_machine_type

        }
        return report_obj.render('cmms.report_partsby_producttype_summary_template', docargs)

    def _get_report_data(self,data):
        _start_date = self._context.get('from_date')
        _end_date = self._context.get('to_date')
        self._inv_lines = self.env['cmms.store.invoice.line'].search([('invoice_date', '>=', _start_date),
                                                                      ('invoice_date', '<=', _end_date)])
        _partTypes = self._inv_lines.mapped('spare_part_type_id')
        return _partTypes

    def _get_parts_total(self, _type):
        _total = sum([x.amount for x in self._inv_lines if x.spare_part_type_id.id == _type])
        return _total

    def _get_categories(self, _ptype ,_mtype=None):
        if _mtype:
            _categs = self._inv_lines.filtered(lambda r: r.spare_part_type_id.id == _ptype and r.machine_id.type_id.id == _mtype).mapped('machine_id.category_id')
        else:
            _categs = self._inv_lines.filtered(lambda r: r.spare_part_type_id.id == _ptype).mapped('machine_id.category_id')
        _categ_sort = _categs.sorted(lambda c: c.name)
        return _categ_sort


    def _get_machine_types(self):
        _categs = self._inv_lines.mapped('machine_id.type_id')
        return _categs

    def _get_ptypes_for_mtype(self,categ):
        _types = self._inv_lines.filtered(lambda r: r.machine_id.type_id.id == categ).mapped('spare_part_type_id')
        return _types

    def _get_total_for_machine_type_prod_type(self, _type, _mtype):
        _total = sum([x.amount for x in self._inv_lines if x.spare_part_type_id.id == _type and x.machine_id.type_id.id == _mtype])
        return _total

    def _get_total_for_machine_type(self, _machinetype):
        _total = sum([x.amount for x in self._inv_lines if x.machine_id.type_id.id == _machinetype])
        return _total

    
    def _get_machines(self, _type, _categ, _mtype= None):
        if _mtype:
            _machines = self._inv_lines.filtered(lambda r: r.machine_id.category_id.id == _categ and r.machine_id.type_id.id == _mtype and r.spare_part_type_id.id == _type).mapped('machine_id')
        else:
            _machines = self._inv_lines.filtered(lambda  r: r.machine_id.category_id.id == _categ and r.spare_part_type_id.id == _type).mapped('machine_id')
        return _machines

    def _get_invoices(self, _machine, _ptype):
        _invoices = self._inv_lines.filtered(lambda r: r.machine_id == _machine and r.spare_part_type_id.id == _ptype)
        return _invoices

    def _get_grand_total(self):
        _total = sum([x.amount for x in self._inv_lines])
        return _total