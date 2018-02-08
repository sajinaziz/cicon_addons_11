from odoo import api, models

_res_openerp_data = []

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
        _res = {}
        _qry = "EXEC dbo.Get_Aging @SunAccountNo = ''"
        _res_qry = self.env['odbc.db.source'].fetch_data('SUN_DB', _qry)
        #_res_qry = [{'a': 1, 'b': 2}]
        if _res_qry:
            _res = _res_qry
        return _res

    def _get_all_partners_from_openerp(self):
        _qry = "SELECT * FROM GetOpenErpData('')"
        _cr = self._cr
        _cr.execute(_qry)
        _res = _cr.dictfetchall()
        return _res

    def _get_report_data(self, _partner=None):
        # _res =[]
        # if _partner.sun_account_ids:
        #     for sun_account in _partner.sun_account_ids:
        #         _res.append(self._get_sun_data(sun_account.sun_account_no))
        # else:
        #     _res = self._get_all_sun_data()
        #self._res_sun_data = self._get_all_sun_data()
        # for _r in _res_sun_data:
        #     for _key in [*_r]:
        #         if _r[_key] == 0 or _r[_key] == '0.0' or _r[_key] == '0':
        #             _r[_key] = 0
        self._res_openerp_data = self._get_all_partners_from_openerp()

    def _get_partners(self):
        _res_list = [(_partner.get('id'), _partner.get('name')) for _partner in self._res_openerp_data]
        _res_set = list(set(_res_list))
        _res = sorted(_res_set, key=lambda x: x[1])
        return _res

    def _get_report_check_data_for_partner(self, partner_id):
        _check_data = list(filter(lambda d: d['id'] == partner_id,  self._res_openerp_data))
        return _check_data


    @api.multi
    def get_report_values(self, docids, data=None):
        _company = self.env['res.company'].search([('id', 'in', docids)])
        self._get_report_data()

        return {
            'doc_ids': _company.ids,
            'doc_model': 'res.partner',
            'docs': _company,
            'get_partners': self._get_partners,
            'get_check_details': self._get_report_check_data_for_partner,
            'get_sun_details': self._get_sun_data

        }
