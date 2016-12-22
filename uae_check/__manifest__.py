# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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
{
    'name': 'UAE Check Writing',
    'version': '1.1',
    'author': 'OpenERP SA, NovaPoint Group',
    'category': 'Generic Modules/Accounting',
    'description': """
Module for the UAE Check Writing and Check Printing.
    """,
    'website': 'http://www.openerp.com',
   # 'depends' : ['account_check_writing','project','cic_sun'],
    'depends' : ['account_voucher','project','cic_sun'],
    # "data":[ "security/uae_check_security.xml" , "security/ir.model.access.csv", "uae_check_view.xml", "cic_res_partner_view.xml",
    #          "check_replace_view.xml",'cic_check_aging_view.xml','report.xml' ],
    "data": ['views/uae_check_view.xml',
             'views/check_replace_view.xml',
             'views/cic_check_aging_view.xml',
             'views/report.xml',
             'report/cheque_receipt_voucher.xml',
             'security/uae_check_security.xml',
             'security/ir.model.access.csv'],
    'test': [],
    'installable': True,
    'active': False,
}