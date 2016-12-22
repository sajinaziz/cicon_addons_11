# -*- coding: utf-8 -*-
##############################################################################
#
#    Daniel Reis
#    2011
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

import os
import sys
from datetime import datetime,date,timedelta
from odoo import models, fields,api
import pyodbc


import logging
_logger = logging.getLogger(__name__)

CONNECTORS = []
try:
    import pyodbc
    CONNECTORS.append( ('pyodbc', 'ODBC') )
except:
    _logger.info('ODBC libraries not available. Please install "unixodbc" and "python-pyodbc" packages.')

try:
    import cx_Oracle
    CONNECTORS.append( ('cx_Oracle', 'Oracle') )
except:
    _logger.info('Oracle libraries not available. Please install "cx_Oracle" python package.')

class ImportOdbcDbsource(models.Model):
    _name="import.odbc.dbsource"
    _description = 'Import Database Source'
    # _columns = {
    #     'name': fields.char('Datasource name', required=True, size=64),
    #     'conn_string': fields.text('Connection string'),
    #     'password': fields.char('Password' , size=40),
    #     'dbtable_ids': fields.one2many('import.odbc.dbtable', 'dbsource_id', 'Import tables'),
    #     'connector': fields.selection(CONNECTORS, 'Connector', required=True),
    # }

    name = fields.Char(string='Datasource name', required=True, size=64)
    conn_string = fields.Text(string='Connection string')
    password = fields.Char(string='Password', size=40)
    dbtable_ids =  fields.One2many('import.odbc.dbtable', 'dbsource_id', 'Import tables')
    connector = fields.Selection(CONNECTORS , required=True)

    #Run all imports
        #Open connection
        #Get all tables to import
        #For each table, run table import (on dbtable model)
        #Close connection
        
    # def conn_open(self, cr, uid, id1):
    #     #Get dbsoource record
    #     data = self.browse(cr, uid, id1)
    #     #Build the full connection string
    #     connStr = data.conn_string
    #     if data.password:
    #         if '%s' not in data.conn_string:
    #             connStr += ';PWD=%s'
    #         connStr = connStr % data.password
    #     #Try to connect
    #     if data.connector == 'cx_Oracle':
    #         os.environ['NLS_LANG'] = 'AMERICAN_AMERICA.UTF8'
    #         conn = cx_Oracle.connect(connStr)
    #     else:
    #         conn = pyodbc.connect(connStr)
    #     #If no exception raise, return ok
    #     return conn

    def conn_open(self):
        #Get dbsoource record

        #Build the full connection string
        connStr = self.conn_string
        print connStr
        if self.password:
            if '%s' not in self.conn_string:
                connStr += ';PWD=%s'
            connStr = connStr % self.password
        if isinstance(connStr, unicode):
            connStr = connStr.encode('utf8')

        #Try to connect
        if self.connector == 'cx_Oracle':
            os.environ['NLS_LANG'] = 'AMERICAN_AMERICA.UTF8'
            conn = cx_Oracle.connect(connStr)
        else:
            conn = pyodbc.connect(connStr)
        print conn
        #If no exception raise, return ok
        return conn

    # def connection_test(self, cr, uid, ids, context=None):
    #     #Perform the test for each selected "dbsource"
    #     data = self.browse(cr, uid, ids)
    #     for obj in data:
    #         #pdb.set_trace()
    #         conn = self.conn_open(cr, uid, obj.id)
    #         conn.close()
    #     #If no exception raise, return ok
    #     return True

    @api.multi
    def connection_test(self):
        #Perform the test for each selected "dbsource"
        for obj in self:
            #pdb.set_trace()
            conn = self.conn_open()
            #print conn
            conn.close()
        #If no exception raise, return ok
        return True
    
    # def import_run(self, cr, uid, ids, context=None):
    #     #Prepare objects to be used
    #     table_obj = self.pool.get('import.odbc.dbtable')
    #     #Import each selected dbsource
    #     data = self.browse(cr, uid, ids)
    #     for obj in data:
    #         #Get list of tables
    #         table_ids = [x.id for x in obj.dbtable_ids]
    #         #Run import
    #         table_obj.import_run( cr, uid, table_ids)
    #     return True

    @api.multi
    def import_run(self):
        #Prepare objects to be used
        # print  "Import Run"
        table_obj = self.env['import.odbc.dbtable']
        #Import each selected dbsource
        for obj in self:
            #Get list of tables
            table_ids = [x.id for x in obj.dbtable_ids]
            #print table_ids
            #Run import
            table_obj.import_run(table_ids)
        return True

    # def fetch_data(self, cr, uid, dbsource=None, query=None, context=None):
    #
    #     dbsource_id = self.search(cr, uid, [('name', '=', dbsource)])
    #     data = self.browse(cr, uid, dbsource_id)
    #     try:
    #         for obj in data:
    #             conn = self.conn_open(cr, uid, obj.id)
    #             db_cursor = conn.cursor()
    #             db_cursor.execute(query)
    #             datarow = []
    #             cols = [x[0] for x in db_cursor.description]
    #             for row in db_cursor:
    #                 columns = {}
    #                 for col in cols:
    #                     columns.update({col: getattr(row, col)})
    #                 datarow.append(columns)
    #     except Exception, error:
    #         raise osv.except_osv(
    #             ("connection test failed"),
    #             ("Reason: %s") % error
    #         )
    #     return datarow


    def fetch_data(self, dbsource=None, query=None):
        print 'In FetchData'
        datarow = []
        data = self.search([('name', '=', dbsource)])
        try:
            for obj in data:
                conn = obj.conn_open()
                db_cursor = conn.cursor()
                db_cursor.execute(query)
                cols = [x[0] for x in db_cursor.description]
                for row in db_cursor:
                    print row
                    columns = {}
                    for col in cols:
                        columns.update({col: getattr(row, col)})
                    datarow.append(columns)
        except Exception,error:
            raise UserWarning(
                ("connection test failed"),
                ("Reason: %s") % error
            )
        return datarow

ImportOdbcDbsource()


class ImportOdbcDbtable(models.Model):
    _name="import.odbc.dbtable"
    _description = 'Import Table Data'
    _order = 'exec_order'
    # _columns = {
    #     'name': fields.char('Datasource name', required=True, size=64),
    #     'enabled': fields.boolean('Execution enabled'),
    #     'dbsource_id': fields.many2one('import.odbc.dbsource', 'Database source', required=True),
    #     'sql_source': fields.text('SQL', required=True, help='Column names must be valid "import_data" columns.'),
    #     'model_target': fields.many2one('ir.model','Target object'),
    #     'noupdate': fields.boolean('No updates', help="Only create new records; disable updates to existing records."),
    #     'exec_order': fields.integer('Execution order', help="Defines the order to perform the import"),
    #     'last_sync': fields.datetime('Last sync date', help="Datetime for the last succesfull sync. Later changes on the source may not be replicated on the destination"),
    #     'last_run': fields.datetime('Last run', readonly=True),
    #     'last_record_count': fields.integer('Last record count', readonly=True),
    #     'last_error_count': fields.integer('Last error count', readonly=True),
    #     'last_warn_count': fields.integer('Last warning count', readonly=True),
    #     'last_log': fields.text('Last run log', readonly=True),
    #     'ignore_rel_errors': fields.boolean('Ignore relationship errors',
    #         help="On error try to reimport rows ignoring relationships."),
    #     'raise_import_errors': fields.boolean('Raise import errors',
    #         help="Import errors not handled, intended for debugging purposes."),
    # }


    name = fields.Char(string='Datasource name', required=True, size=64)
    enabled = fields.Boolean(string='Execution enabled', default=True)
    dbsource_id = fields.Many2one('import.odbc.dbsource', string='Database source', required=True)
    sql_source = fields.Text(string='SQL', required=True, help='Column names must be valid "import_data" columns.')
    model_target = fields.Many2one('ir.model', string='Target object')
    noupdate = fields.Boolean(string='No updates', help="Only create new records; disable updates to existing records.")
    exec_order = fields.Integer(string='Execution order', help="Defines the order to perform the import",default=10)
    last_sync = fields.Date(string='Last sync date',help="Datetime for the last succesfull sync. Later changes on the source may not be replicated on the destination",default=fields.Date.context_today)
    last_run = fields.Date(string='Last run', readonly=True,default=fields.Date.context_today)
    last_record_count = fields.Integer(string='Last record count', readonly=True)
    last_error_count = fields.Integer(string='Last error count', readonly=True)
    last_warn_count = fields.Integer(string='Last warning count', readonly=True)
    last_log = fields.Text(string='Last run log', readonly=True)
    ignore_rel_errors = fields.Boolean(string='Ignore relationship errors',help="On error try to reimport rows ignoring relationships.")
    raise_import_errors = fields.Boolean(string='Raise import errors',help="Import errors not handled, intended for debugging purposes.")

    # _defaults = {
    #     'enabled': True,
    #     'exec_order': 10,
    # }

    #TODO: allow differnt cron jobs to run different sets of imports
    #TODO: add field for user-friendly error report, to be used in automatic e-mail
    #TODO: create "clean-up" procedure, to act on (inactivate?) each record without correspondence in the SQL results 
    
#     def import_run(self, cr, uid, ids=None, context=None):
#         #TODO: too many lines and indent levels - please refactor me!
#         def is_id_field(x):
#             """"Detect is the column is a one2many field"""
#             return len(x)>3 and x[-3:] == ':id' or x[-3:] == '/id'
#
#         def remove_cols(ids, cols, data):
#             """Remove ids cols and data lists"""
#             rc, rd = list(), list()
#             for c, d in zip(cols, data):
#                 if c not in ids:
#                     rc.append(c)
#                     rd.append(d)
#             return rc, rd
#
#         def safe_import(cr, uid, colrow, datarows, noupdate, raise_import_errors=False):
#             """Import data and returns error msg or empty string"""
#             res = ''
#             if raise_import_errors:
#                 model_obj.import_data(cr, uid, colrow, datarows, noupdate=obj.noupdate)
#             else:
#                 try:
#                     model_obj.import_data(cr, uid, colrow, datarows, noupdate=obj.noupdate)
#                 except:
#                     res = str(sys.exc_info()[1])
#             return res
#
#         def text_to_log(level, obj_id = '', msg = '', rel_id = ''):
#             if '_id_' in obj_id:
#                 obj_id = '.'.join(obj_id.split('_')[:-2]) \
#                        + ': ' + obj_id.split('_')[-1]
#             if ': .' in msg and not rel_id:
#                 rel_id = msg[msg.find(': .')+3:]
#                 if '_id_' in rel_id:
#                     rel_id = '.'.join(rel_id.split('_')[:-2]) \
#                            + ': ' + rel_id.split('_')[-1]
#                     msg = msg[:msg.find(': .')]
#             return '%s|%s\t|%s\t|%s' % (level.ljust(5), obj_id, rel_id, msg)
# #            return '%s|%s|%s|%s' % (
# #                level.ljust(5, filler),
# #                obj_id.ljust(28, filler),
# #                rel_id.ljust(28, filler),
# #                msg )
#
#         #Prepare support objects
#         dbsource_obj = self.pool.get('import.odbc.dbsource')
#         _logger.debug('Starting import run...')
#         #Build id list if none is provided
#         if not ids:
#             ids = self.search(cr, uid, [('enabled', '=', True)])
#         #Consider each dbtable:
#         data = self.browse(cr, uid, ids)
#         for obj in data:
#             #Now without seconds (avoid problems with SQL smalldate)
#             #TODO: convert UTC Now to local timezone (http://stackoverflow.com/questions/4770297/python-convert-utc-datetime-string-to-local-datetime)
#             dt_now = datetime.datetime.now()
#             dt_now = dt_now.replace(second=0, microsecond=0)
#             ignore_rel_errors = obj.ignore_rel_errors
#             raise_import_errors = obj.raise_import_errors
#             #Prepare log to write
#             log = {
#                 'last_run': dt_now,
#                 'last_record_count': 0,
#                 'last_error_count': 0,
#                 'last_warn_count': 0,
#                 'last_log': ''
#                 }
#             log_lines = list()
#             #Skip if it's inactive
#             if obj.enabled:
#                 #Prepare SQL sentence; replace every "?" with the last_sync date
#                 sql = obj.sql_source
#                 dt  = obj.last_sync
#                 params = tuple( [dt] * sql.count('?') )
#                 #Open source connection
#                 conn = dbsource_obj.conn_open(cr, uid, obj.dbsource_id.id)
#                 #Get source data cursor
#                 db_cursor = conn.cursor()
#                 db_cursor.execute(sql, params)
#                 #Build column list from cursor:
#                 # - exclude columns titled "None"
#                 # - add an extra "id" for the xml_id
#                 cols = [x[0] for x in db_cursor.description if x[0].upper() != 'NONE']
#                 cols.append('id')
#                 #Get destination object
#                 model = obj.model_target.model
#                 model_obj = self.pool.get(model)
#                 #Setup prefix to use in xml_ids
#                 xml_prefix = model.replace('.', '_') + "_id_"
#                 #Import each row:
#                 for row in db_cursor:
#                     #Build data row
#                     datarow = []
#                     for (i, col) in enumerate(row):
#                         #import only columns present in the "cols" list
#                         if db_cursor.description[i][0] in cols:
#                             #TODO: Handle datetimes properly - convert from localtime to UTC!
#                             datarow.append( str(col).strip() )
#                     #import pdb; pdb.set_trace()
#                     #Add "xml_id" column to row
#                     datarow.append( xml_prefix + str(row[0]).strip() )
#
#                     #Import the row; on error, write line to the log
#                     log['last_record_count'] += 1
#                     err = safe_import(cr, uid, cols, [datarow], obj.noupdate, raise_import_errors)
#
#                     #If error; retry ignoring many2one fields...
#                     if err and ignore_rel_errors:
#                         #Log a warning
#                         log_lines.append( text_to_log('WARN', datarow[-1], err ) )
#                         log['last_warn_count'] += 1
#                         #Try ignoring each many2one (tip: in SQL select problematic FKs first)
#                         idcols = filter(is_id_field, cols)
#                         for idcol in idcols:
#                             c, d = remove_cols( [idcol], cols, datarow)
#                             err = safe_import(cr, uid, c, [d], obj.noupdate, raise_import_errors)
#                             if not err: break
#                         #If still error; retry ignoring all ".../id" fields
#                         if err:
#                             c, d = remove_cols( idcols, cols, datarow)
#                             err = safe_import(cr, uid, c, [d], obj.noupdate, raise_import_errors)
#                     #If still error after all import tries, reject data row
#                     if err:
#                         _logger.debug('%s =>\t%s' % (err, datarow) )
#                         log_lines.append( text_to_log('ERROR', datarow[-1], err ) )
#                         log['last_error_count'] += 1
#                     #Inform progress on long Imports, every 500 rows
#                     if log['last_record_count'] % 500 == 0:
#                         _logger.info('...%s rows processed...' % (log['last_record_count']) )
#
#                 #Finished importing all rows
#                 msg = 'Imported %s , %s rows, %s errors, %s warnings.' % (
#                     model,
#                     log['last_record_count'],
#                     log['last_error_count'] ,
#                     log['last_warn_count'] )
#                 #Close the connection
#                 conn.close()
#                 #If no errors, write new sync date
#                 if not (log['last_error_count'] or log['last_warn_count']):
#                     _logger.debug(msg)
#                     log['last_sync'] = log['last_run']
#                 level = logging.INFO
#                 if log['last_warn_count']: level = logging.WARN
#                 if log['last_error_count']: level = logging.ERROR
#                 _logger.log(level, msg)
#             #Write run log, either if the table import is active or inactive
#             if log_lines:
#                  log_lines.insert(0, text_to_log('LEVEL', '== Line ==    ','== Relationship ==','== Message =='))
#                  log.update( {'last_log': '\n'.join(log_lines)} )
#             self.write(cr, uid, [obj.id], log)
#         #Finished
#         return True

    @api.multi
    def Save_Data(self):
        dbsource_obj = self.env['import.odbc.dbsource']
        for obj in self:
            if obj.enabled:
                # Prepare SQL sentence; replace every "?" with the last_sync date
                sql = obj.sql_source
                dt = obj.last_sync
                params = tuple([dt] * sql.count('?'))
                # Open source connection
                conn = self.dbsource_id.conn_open()
                # Get source data cursor
                db_cursor = conn.cursor()
                db_cursor.execute(sql)
                rows = db_cursor.fetchall()
                for row in rows:
                    data_list = {'id':row[0],'name': row[1]}
                    print data_list
                return data_list




    @api.multi
    def import_run(self):
        print self.ids
        # TODO: too many lines and indent levels - please refactor me!
        def is_id_field(x):
            """"Detect is the column is a one2many field"""
            return len(x) > 3 and x[-3:] == ':id' or x[-3:] == '/id'

        def remove_cols(ids, cols, data):
            """Remove ids cols and data lists"""
            rc, rd = list(), list()
            for c, d in zip(cols, data):
                if c not in ids:
                    rc.append(c)
                    rd.append(d)
            return rc, rd

        def safe_import(colrow, datarows, noupdate, raise_import_errors=False):
            """Import data and returns error msg or empty string"""
            res = ''
            if raise_import_errors:
                model_obj.import_data(colrow, datarows, noupdate=obj.noupdate)
            else:
                try:
                    model_obj.import_data(colrow, datarows, noupdate=obj.noupdate)
                except:
                    res = str(sys.exc_info()[1])
            return res

        def text_to_log(level, obj_id='', msg='', rel_id=''):
            if '_id_' in obj_id:
                obj_id = '.'.join(obj_id.split('_')[:-2]) \
                         + ': ' + obj_id.split('_')[-1]
            if ': .' in msg and not rel_id:
                rel_id = msg[msg.find(': .') + 3:]
                if '_id_' in rel_id:
                    rel_id = '.'.join(rel_id.split('_')[:-2]) \
                             + ': ' + rel_id.split('_')[-1]
                    msg = msg[:msg.find(': .')]
            return '%s|%s\t|%s\t|%s' % (level.ljust(5), obj_id, rel_id, msg)
            #            return '%s|%s|%s|%s' % (
            #                level.ljust(5, filler),
            #                obj_id.ljust(28, filler),
            #                rel_id.ljust(28, filler),
            #                msg )

        # Prepare support objects
        dbsource_obj = self.env['import.odbc.dbsource']
        _logger.debug('Starting import run...')
        # Build id list if none is provided
        if not self.ids:
            ids = self.search([('enabled', '=', True)])
        # Consider each dbtable:
        #data = self.browse(ids)
        for obj in self:
            # Now without seconds (avoid problems with SQL smalldate)
            # TODO: convert UTC Now to local timezone (http://stackoverflow.com/questions/4770297/python-convert-utc-datetime-string-to-local-datetime)
            dt_now = datetime.today()
            dt_now = dt_now.replace(second=0, microsecond=0)
            ignore_rel_errors = obj.ignore_rel_errors
            raise_import_errors = obj.raise_import_errors
            # Prepare log to write
            log = {
                'last_run': dt_now,
                'last_record_count': 0,
                'last_error_count': 0,
                'last_warn_count': 0,
                'last_log': ''
            }
            log_lines = list()
            # Skip if it's inactive
            if obj.enabled:
                # Prepare SQL sentence; replace every "?" with the last_sync date
                sql = obj.sql_source
                dt = obj.last_sync
                params = tuple([dt] * sql.count('?'))
                # Open source connection
                conn = self.dbsource_id.conn_open()
                # Get source data cursor
                db_cursor = conn.cursor()
                db_cursor.execute(sql, params)
                # Build column list from cursor:
                # - exclude columns titled "None"
                # - add an extra "id" for the xml_id
                cols = [x[0] for x in db_cursor.description if x[0].upper() != 'NONE']
                cols.append('id')
                # Get destination object
                model = obj.model_target.model
                model_obj = self.env[model]
                # Setup prefix to use in xml_ids
                xml_prefix = model.replace('.', '_') + "_id_"
                # Import each row:
                for row in db_cursor:
                    # Build data row
                    datarow = []
                    for (i, col) in enumerate(row):
                        # import only columns present in the "cols" list
                        if db_cursor.description[i][0] in cols:
                            # TODO: Handle datetimes properly - convert from localtime to UTC!
                            datarow.append(str(col).strip())
                    # import pdb; pdb.set_trace()
                    # Add "xml_id" column to row
                    datarow.append(xml_prefix + str(row[0]).strip())

                    # Import the row; on error, write line to the log
                    log['last_record_count'] += 1
                    err = safe_import(cols, [datarow], obj.noupdate, raise_import_errors)

                    # If error; retry ignoring many2one fields...
                    if err and ignore_rel_errors:
                        # Log a warning
                        log_lines.append(text_to_log('WARN', datarow[-1], err))
                        log['last_warn_count'] += 1
                        # Try ignoring each many2one (tip: in SQL select problematic FKs first)
                        idcols = filter(is_id_field, cols)
                        for idcol in idcols:
                            c, d = remove_cols([idcol], cols, datarow)
                            err = safe_import(c, [d], obj.noupdate, raise_import_errors)
                            if not err: break
                        # If still error; retry ignoring all ".../id" fields
                        if err:
                            c, d = remove_cols(idcols, cols, datarow)
                            err = safe_import(c, [d], obj.noupdate, raise_import_errors)
                    # If still error after all import tries, reject data row
                    if err:
                        _logger.debug('%s =>\t%s' % (err, datarow))
                        log_lines.append(text_to_log('ERROR', datarow[-1], err))
                        log['last_error_count'] += 1
                    # Inform progress on long Imports, every 500 rows
                    if log['last_record_count'] % 500 == 0:
                        _logger.info('...%s rows processed...' % (log['last_record_count']))

                # Finished importing all rows
                msg = 'Imported %s , %s rows, %s errors, %s warnings.' % (
                    model,
                    log['last_record_count'],
                    log['last_error_count'],
                    log['last_warn_count'])
                # Close the connection
                conn.close()
                # If no errors, write new sync date
                if not (log['last_error_count'] or log['last_warn_count']):
                    _logger.debug(msg)
                    log['last_sync'] = log['last_run']
                level = logging.INFO
                if log['last_warn_count']: level = logging.WARN
                if log['last_error_count']: level = logging.ERROR
                _logger.log(level, msg)
            # Write run log, either if the table import is active or inactive
            if log_lines:
                log_lines.insert(0, text_to_log('LEVEL', '== Line ==    ', '== Relationship ==', '== Message =='))
                log.update({'last_log': '\n'.join(log_lines)})
            self.write(log)
        # Finished
        return True

    @api.multi
    def import_schedule(self,  ids, context=None):
        cron_obj = self.env['ir.cron']
        new_create_id = cron_obj.create({
            'name': 'Import ODBC tables',
            'interval_type': 'hours',
            'interval_number': 1, 
            'numbercall': -1,
            'model': 'import.odbc.dbtable',
            'function': 'import_run', 
            'doall': False,
            'active': True
            })
        return {
            'name': 'Import ODBC tables',
            'view_type': 'form',
            'view_mode': 'form,tree',
            'res_model': 'ir.cron',
            'res_id': new_create_id,
            'type': 'ir.actions.act_window',
            }
ImportOdbcDbtable()
