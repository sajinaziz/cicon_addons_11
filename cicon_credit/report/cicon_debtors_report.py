from odoo import api, models


class CiconDebtorsReport(models.AbstractModel):
    _name = 'report.cicon_credit.report_cicon_debtors_report_template'

    def _get_sun_data(self,sun_account):
        _res = {}
        _qry = "EXEC dbo.Get_Aging @SunAccountNo = '" + sun_account + "'"
        _res_qry = self.env['odbc.db.source'].fetch_data('SUN_DB', _qry)
        #_res_qry = [{'a': 1, 'b': 2}]
        print(_res_qry)
        if _res_qry:
            _res = _res_qry[0]
        return _res

    def _get_report_data(self, _partner):
        _res =[]
        for sun_account in _partner.sun_account_ids:
            _res.append(self._get_sun_data(sun_account.sun_account_no))
        return _res

    @api.multi
    def get_report_values(self, docids, data=None):
        _partners = self.env['res.partner'].search([('id', 'in', docids)])

        return {
            'doc_ids': _partners.ids,
            'doc_model': 'res.partner',
            'docs': _partners,
            'get_report_data': self._get_report_data
        }