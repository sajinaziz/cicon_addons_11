# -*- coding: utf-8 -*-
##############################################################################
#
#   Copyright (c) 2011 Camptocamp SA (http://www.camptocamp.com)
#   @author Nicolas Bessi, Vincent Renaville, Guewen Baconnier
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import time

from openerp.report import report_sxw
from openerp import pooler


class CheckRecieptReport(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(CheckRecieptReport, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({'time': time,
                                  'getSelectionValue': self.getSelectionValue})

    def getSelectionValue(self,model,fieldName,field_val):
                return dict(self.pool.get(model).fields_get(self.cr, self.uid)[fieldName]['selection'])[field_val]

    # ${getSelectionValue('sale.order','order_type',order.order_type)}

report_sxw.report_sxw('uae_check.cheque_receipt_voucher',
                      'cic.check.receipt',
                      'uae_check/report/cheque_receipt_voucher.mako',
                      parser=CheckRecieptReport)
