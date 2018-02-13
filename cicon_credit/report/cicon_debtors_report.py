from odoo import api, models
import decimal
_res_openerp_data = []
_res_sun_data = []


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

    def _get_partners(self):
        _res_list = [(_partner.get('id'), _partner.get('name')) for _partner in self._res_openerp_data]
        _res_set = list(set(_res_list))
        _res = sorted(_res_set, key=lambda x: x[1])
        return _res

    def _get_report_check_data_for_partner(self, partner_id):
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
            if _sun_data:
                for k in _sun_data.keys():
                    if isinstance(_sun_data.get(k), decimal.Decimal):
                        _sun_data[k] = float(_sun_data.get(k))
                _check.update(_sun_data)
                _res.append(_check)
        return _res

    @api.multi
    def get_report_values(self, docids, data=None):
        _filter =''
        if data.get('form'):
            _filter = ",@Fromdt='" + data['form'].get('start_date') + "' ,@Todt='" + data['form'].get('end_date') + "'"
        print(_filter)
        self._get_report_data(_filter)
        return {
            'data':data,
            'get_partners': self._get_partners,
            'get_check_details': self._get_report_check_data_partner_with_sun,
        }
