from odoo import models, api

_inv_lines = None


class InventoryExpenseReports(models.AbstractModel): # Report File Name
    _name = 'report.cmms.cmms_inventory_expense_report_summary'

    @api.model
    def render_html(self,docids, data=None):
        data = data if data is not None else {}
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('cmms.cmms_inventory_expense_report_summary')
        _docs = self._get_report_data(data.get('ids', data.get('active_ids')))
        docargs = {
            'doc_ids': data.get('ids', data.get('active_ids')),
            'doc_model': report.model,
            'docs': _docs,
            'heading': self._context.get('heading'),
            'show_summary': self._context.get('show_summary'),
            'get_category': self._get_categories,
            'get_machine': self._get_machines,
            'get_invoice': self._get_invoices,
            'get_total_machine': self._get_invoice_total_machine,
            'get_total_categ': self._get_invoice_total_categ,
            'get_total_type': self._get_invoice_total_type,
            'get_grand_total': self._get_grand_total

        }
        return report_obj.render('cmms.cmms_inventory_expense_report_summary', docargs)

    def _get_report_data(self,data):
        _start_date = self._context.get('from_date')
        _end_date = self._context.get('to_date')
        _qry = [('invoice_date', '>=', _start_date),('invoice_date', '<=', _end_date)]
        if self._context.get('company_id'):
            _qry.append(('company_id','=', self._context.get('company_id')))
        self._inv_lines = self.env['cmms.store.invoice.line'].search(_qry)
        _types = self._inv_lines.mapped('machine_id.type_id')
        return _types

    def _get_categories(self, _type):
        _categs = self._inv_lines.filtered(lambda r: r.machine_id.type_id == _type).mapped('machine_id.category_id').sorted(key=lambda r: r.name)
        return _categs

    def _get_machines(self, _type, _categ):
        _machines = self._inv_lines.filtered(lambda r: r.machine_id.category_id == _categ and r.machine_id.type_id == _type).mapped('machine_id')
        return _machines

    def _get_invoices(self, _machine):
        _invoices = self._inv_lines.filtered(lambda r: r.machine_id == _machine)
        return _invoices

    def _get_invoice_total_machine(self, _machine):
        _total = sum(x.amount for x in self._inv_lines.filtered(lambda r: r.machine_id == _machine))
        return _total

    def _get_invoice_total_categ(self, _categ, _type):
        _total = sum(x.amount for x in self._inv_lines.filtered(lambda r: r.machine_id.category_id == _categ and r.machine_id.type_id == _type))
        return _total

    def _get_invoice_total_type(self, _type):
        _total = sum(x.amount for x in self._inv_lines.filtered(lambda r: r.machine_id.type_id == _type))
        return _total

    def _get_grand_total(self):
        _total = sum(x.amount for x in self._inv_lines)
        return _total










