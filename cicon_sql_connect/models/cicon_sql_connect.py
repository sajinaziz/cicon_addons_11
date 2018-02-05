import os
from odoo import models, fields, api

import logging

_logger = logging.getLogger(__name__)

CONNECTORS = []
try:
    import pyodbc

    CONNECTORS.append(('pyodbc', 'ODBC'))
except:
    _logger.info('ODBC libraries not available. Please install "unixodbc" and "python-pyodbc" packages.')

try:
    import cx_Oracle

    CONNECTORS.append(('cx_Oracle', 'Oracle'))
except:
    _logger.info('Oracle libraries not available. Please install "cx_Oracle" python package.')


class OdbcDbSource(models.Model):
    _name = "odbc.db.source"
    _description = 'Database Source'
    name = fields.Char(string='Datasource name', required=True, size=64)
    conn_string = fields.Text(string='Connection string')
    password = fields.Char(string='Password', size=40)
    connector = fields.Selection(CONNECTORS, required=True)

    @api.multi
    def conn_open(self):
        self.ensure_one()
        # Get dbsoource record
        # Build the full connection string
        connStr = self.conn_string
        if self.password:
            if '%s' not in self.conn_string:
                connStr += ';PWD=%s'
            connStr = connStr % self.password

        # Try to connect
        if self.connector == 'cx_Oracle':
            os.environ['NLS_LANG'] = 'AMERICAN_AMERICA.UTF8'
            conn = cx_Oracle.connect(connStr)
        else:
            conn = pyodbc.connect(connStr)
        # If no exception raise, return ok
        return conn

    @api.multi
    def connection_test(self):
        # Perform the test for each selected "dbsource"
        for obj in self:
            # pdb.set_trace()
            conn = self.conn_open()
            # print conn
            conn.close()
        # If no exception raise, return ok
        return True

    def fetch_data(self, dbsource=None, query=None):
        datarow = []
        data = self.search([('name', '=', dbsource)])
        try:
            for obj in data:
                conn = obj.conn_open()
                db_cursor = conn.cursor()
                db_cursor.execute(query)
                cols = [x[0] for x in db_cursor.description]
                for row in db_cursor:
                    columns = {}
                    for col in cols:
                        columns.update({col: getattr(row, col)})
                    datarow.append(columns)
        except Exception:
            raise UserWarning(
                ("connection test failed"),
                ("Reason: %s") % Exception
            )
        return datarow
