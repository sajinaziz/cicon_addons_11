from odoo import models, fields, api


class DrawingCreator(models.Model):
    """
     Wizard helper for creating Drawing list
       Refer creating function on 'tech.submittal.revision' onchange_drawing
    """
    _name = "tech.drawing.creator"
    _description = "Drawing Creator"

    start_no = fields.Integer('Start No', required=True, help="Start Number of Document in digit eg:- 101")
    end_no = fields.Integer('End No', required=True, help="End Number of Document in digit eg:- 111")
    # renamed Prefix Field as many2many_tags widget not support _rec_name concept on build : 20151011
    name = fields.Char('Document Prefix', size=32, required=False,
                       help="Prefix of Document without separator('-','/') eg:- DWG")
    suffix = fields.Char('Document Suffix', size=32, required=False,
                         help="Suffix of Document without separator('-','/') eg:- DWG")
    status = fields.Char('Revision Status', size=32,
                         help="Revision Status to display for Document eg:- Rev.01, Rev-01, R1")
    description = fields.Char('Document Description', required=False,
                              help="Description on Document eg:- Retaining Wall Level 1 ")
    padding_zero = fields.Integer('Zero padding', default=2,
                                  help="pads on the left with zeros to fill eg:- if value is 4 then it shows : 0001"
                                  )

    _sql_constraints = [('padding_count', 'CHECK(padding_zero < 5)', 'Padding Zero Value Should be < 5 ')]

