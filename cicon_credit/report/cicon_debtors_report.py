from odoo import api, models

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

    def _get_all_sun_data(self):
        _qry = "EXEC dbo.Get_Aging @SunAccountNo = ''"
        _res_qry = self.env['odbc.db.source'].fetch_data('SUN_DB', _qry)
        return _res_qry

    def _get_all_partners_from_openerp(self):
        _qry = "SELECT * FROM GetOpenErpData('')"
        _cr = self._cr
        _cr.execute(_qry)
        _res = _cr.dictfetchall()
        return _res

    def _get_report_data(self, _partner=None):
        self._res_sun_data = self._get_all_sun_data()
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
        _res  = []
        _checks  = self._get_report_check_data_for_partner(partner_id)
        for _check in _checks:
            _sun_data = self._get_report_sun_data(_check.get('account_no'))
            if _sun_data:
                _check.update(_sun_data)
                _res.append(_check)
        return _res

    @api.multi
    def get_report_values(self, docids, data=None):
        _company = self.env['res.company'].search([('id', 'in', docids)])
        self._get_report_data()

        return {
            'doc_ids': _company.ids,
            'doc_model': 'res.partner',
            'docs': _company,
            'get_partners': self._get_partners,
            'get_check_details': self._get_report_check_data_partner_with_sun,
        }
