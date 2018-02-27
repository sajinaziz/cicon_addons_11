from odoo import api, models
import decimal
from collections import defaultdict

_res_openerp_data = []
_res_sun_data = []
_res_sun_data_no_partner = []
_sun_codes = []
_valid_datas = []

class CiconDebtorsReport(models.AbstractModel):
    _name = 'report.cicon_credit.report_cicon_debtors_report_template'

    def _get_sun_data(self, sun_account):
        _res = {}
        _qry = "EXEC dbo.Get_Aging @SunAccountNo = '" + sun_account + "'"
        _res_qry = self.env['odbc.db.source'].fetch_data('SUN_DB', _qry)
        #_res_qry = [{'a': 1, 'b': 2}]
        if _res_qry:
            _res = _res_qry[0]
        return _res

    def _get_all_sun_data(self, param):
        _qry = "EXEC dbo.Get_Aging @SunAccountNo = '' "
        if param:
            _qry = _qry + param
        _res_qry = self.env['odbc.db.source'].fetch_data('SUN_DB', _qry)
        for _r in _res_qry:
            self._clean_up_sun_decimal(_r)
        return _res_qry

    def _get_all_partners_from_openerp(self):
        _qry = "SELECT * FROM GetOpenErpData('')"
        _cr = self._cr
        _cr.execute(_qry)
        _res = _cr.dictfetchall()
        return _res

    def _get_report_data(self, param=None):
        self._res_sun_data = self._get_all_sun_data(param)
        self._res_openerp_data = self._get_all_partners_from_openerp()
        self._valid_datas = []

    def _get_partners(self, _report_opt=''):
        _partners=[]
        _dummy_partner = None
        self._sun_codes =[]
        if _report_opt == 'report_sun_aging':
            self._sun_codes = [str(a['ACCNT_CODE']).strip() for a in self._res_sun_data]
            _partners = list(filter(lambda d: d['account_no'] in self._sun_codes ,  self._res_openerp_data))
            _partner_sun_codes = list(set([p['account_no'] for p in self._res_openerp_data]))
            self._res_sun_data_no_partner = list(filter(lambda d: str(d['ACCNT_CODE']).strip() not in _partner_sun_codes,  self._res_sun_data))
            _dummy_partner = (0, '')
        else:
            _partners = self._res_openerp_data
        _res_list = [(_partner.get('id'), _partner.get('name')) for _partner in _partners]
        _res_set = list(set(_res_list))
        _res = sorted(_res_set, key=lambda x: x[1])
        if _report_opt and _dummy_partner:
            _res.append(_dummy_partner)
        return _res

    def _get_report_check_data_for_partner(self, partner_id):
        _check_data =[]
        if self._sun_codes:
            _check_data = list(filter(lambda d: d['id'] == partner_id and d['account_no'] in self._sun_codes,  self._res_openerp_data))
        else:
            _check_data = list(filter(lambda d: d['id'] == partner_id,  self._res_openerp_data))
        return _check_data

    def _get_report_sun_data(self, sun_account):
        _res = {}
        _sun_data = list(filter(lambda d:  str(d['ACCNT_CODE']).strip() == str(sun_account).strip(), self._res_sun_data))
        if _sun_data:
            _res = _sun_data[0]
        return _res

    def _get_report_check_data_partner_with_sun(self, partner_id):
        _res = []
        _checks = self._get_report_check_data_for_partner(partner_id)
        for _check in _checks:
            _sun_data = self._get_report_sun_data(_check.get('account_no'))
            _check.update(_sun_data)
            _res.append(_check)
        if not _checks and partner_id == 0:
            _res = self._res_sun_data_no_partner
        self._valid_datas.extend(_res)
        return _res

    def _get_grand_total(self):
        _key_total = ['total_chq', 'total_lc',  'TOTAL', '30 Days', '30-60 Days', '60-90 Days', '90-120 Days', '120-150 Days', '150-180 Days', '6-12 Months', 'Above Year']
        _d_total = defaultdict(list)
        for _rec in self._valid_datas:
            for k, v in _rec.items():
                if k in _key_total:
                    _d_total[k].append(v)
        return _d_total

    def _clean_up_sun_decimal(self, _sun_data):
        if _sun_data:
            for k in _sun_data.keys():
                if isinstance(_sun_data.get(k), decimal.Decimal):
                    _sun_data[k] = float(_sun_data.get(k))

    @api.multi
    def get_report_values(self, docids, data=None):
        _filter =''

        if data.get('form') and data['form'].get('start_date'):
            _filter = ",@Fromdt='" + data['form'].get('start_date') + "' ,@Todt='" + data['form'].get('end_date') + "'"
        self._get_report_data(_filter)
        return {
            'data': data,
            'get_partners': self._get_partners,
            'get_check_details': self._get_report_check_data_partner_with_sun,
            'get_total': self._get_grand_total
        }

    def _get_key_columns(self):
        _keys = ['name', 'ACCNT_CODE', 'ACCNT_NAME', 'project_name', 'Un Covered Amount', 'total_chq', 'total_lc',  'TOTAL', '30 Days', '30-60 Days', '60-90 Days', '90-120 Days', '120-150 Days', '150-180 Days', '6-12 Months', 'Above Year']
        return _keys

    def get_report_data_export(self, data):
        _filter = ''
        _res = []
        if data.get('start_date') and data.get('end_date'):
            _filter = ",@Fromdt='" + data.get('start_date') + "' ,@Todt='" + data.get('end_date') + "'"
        self._get_report_data(_filter)
        _partners = self._get_partners(data.get('report_option'))
        for _partner in _partners:
            _res.extend(self._get_report_check_data_partner_with_sun(_partner[0]))
        return _res

