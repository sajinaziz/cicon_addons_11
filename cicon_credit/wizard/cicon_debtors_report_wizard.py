from odoo import fields, models, api
from datetime import datetime
import io
import codecs
import xlsxwriter


class CiconDebtorsReportWizard(models.TransientModel):
    _name = 'cicon.debtors.report.wizard'
    _description = "CICON Debtors Report Wizard"
    _rec_name = 'report_option'

    report_option = fields.Selection([('report_sun_check', 'Aging Report (With LC & Check)'),
                                      ('report_sun_aging', 'Aging Report (Sun System)'),
                                      ], string='Report Options',
                                     default='report_sun_check', required=True)
    report_period = fields.Selection([('invoice_date', 'Invoice Date'), ('invoice_period', 'Invoice Period')],
                                     default='invoice_date', string="Report Period")
    start_date = fields.Date('From')
    end_date = fields.Date('To')
    openerp_partner_id = fields.Many2one('openerp.partner', string="Customer", domain="[('customer','=', True)]")

    @api.multi
    def show_report(self):
        _res = None
        if self.report_option != 'report_sun_aging_12months':
            _company = self.env.user.company_id
            data = {'form': {'start_date': '', 'end_date': '', 'report_option': ''}}
            if self.start_date and self.end_date:
                data.update(form={})
                start_date = datetime.strptime(self.start_date, '%Y-%m-%d').strftime('%Y%m%d')
                end_date = datetime.strptime(self.end_date, '%Y-%m-%d').strftime('%Y%m%d')
                data['form'].update(start_date=start_date)
                data['form'].update(end_date=end_date)
            data['form'].update(report_option=self.report_option)
            res = self.env.ref('cicon_credit.action_cicon_debtors_report').report_action(_company,data=data)
        else:
            res = self.env.ref('cicon_credit.action_cicon_debtors_report_12months').report_action(self)
        return res

    def create_excel_data(self,data):
        _rptObj = self.env['report.cicon_credit.report_cicon_debtors_report_template']
        records = _rptObj.get_report_data_export(data)
        print(len(records))
        encoding = 'base64'
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        format1 = workbook.add_format()
        format1.set_num_format('#,##0.00')
        worksheet = workbook.add_worksheet()
        row = 0
        col = 0
        for _k_col in _rptObj._get_key_columns():
            worksheet.write(row, col, _k_col)
            col += 1
        col =0
        for _rec in records:
            row += 1
            worksheet.write(row, 0, _rec.get('name'))
            worksheet.write(row, 1, _rec.get('ACCNT_CODE'))
            worksheet.write(row, 2, _rec.get('ACCNT_NAME'))
            worksheet.write(row, 3, _rec.get('project_name'))
            worksheet.write_number(row, 4, (_rec.get('TOTAL', 0) - (_rec.get('total_chq', 0) + _rec.get('total_lc', 0))), format1)
            worksheet.write_number(row, 5, _rec.get('total_chq', 0), format1)
            worksheet.write_number(row, 6, _rec.get('total_lc', 0), format1)
            worksheet.write_number(row, 7, _rec.get('TOTAL', 0), format1)
            worksheet.write_number(row, 8, _rec.get('30 Days', 0), format1)
            worksheet.write_number(row, 9, _rec.get('30-60 Days', 0), format1)
            worksheet.write_number(row, 10, _rec.get('60-90 Days', 0), format1)
            worksheet.write_number(row, 11, _rec.get('90-120 Days', 0), format1)
            worksheet.write_number(row, 12, _rec.get('120-150 Days', 0), format1)
            worksheet.write_number(row, 13, _rec.get('150-180 Days', 0), format1)
            worksheet.write_number(row, 14, _rec.get('6-12 Months', 0), format1)
            worksheet.write_number(row, 15, _rec.get('Above Year', 0), format1)

        workbook.close()
        output.seek(0)
        vals = {
            'name': 'Debtor Report',
            'datas_fname': 'debtor_report_2018.xlsx',
            'description': 'Debtor Report',
            'type': 'binary',
            'db_datas': codecs.encode(output.read(), encoding),
            'res_name': self.report_option,
            'res_model': 'cicon.debtors.report.wizard',
            'res_id': self.id
        }
        file_id = self.env['ir.attachment'].create(vals)
        return file_id

    @api.multi
    def export_excel(self):
        data = {'start_date': '', 'end_date': '', 'report_option': ''}
        if self.start_date and self.end_date:
            start_date = datetime.strptime(self.start_date, '%Y-%m-%d').strftime('%Y%m%d')
            end_date = datetime.strptime(self.end_date, '%Y-%m-%d').strftime('%Y%m%d')
            data.update(start_date=start_date)
            data.update(end_date=end_date)
        data.update(report_option=self.report_option)
        self.create_excel_data(data)
        form_id = self.env.ref('cicon_credit.cicon_debtors_report_wizard_form_current_view')
        return {
            'name': "Report Wizard",
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': form_id.id,
            'res_model': 'cicon.debtors.report.wizard',
            'res_id': self.id,
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'current'
        }



