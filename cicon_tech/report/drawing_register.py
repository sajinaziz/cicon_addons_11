from odoo import tools
from odoo import models, fields, api


class DrawingRegister(models.Model):
    """ Creates Database view to show drawing registry pivoted view """
    _name = 'tech.drawing.register'
    _description = "Drawing Register"
    _auto = False

    job_site_id = fields.Many2one('cic.job.site',readonly=True)
    submittal_id = fields.Many2one('tech.submittal','Submittal',readonly=True)
    revision_id = fields.Many2one('tech.submittal.revision','Submittal',readonly=True)
    name = fields.Char('Drawing Name', readonly=True)
    description = fields.Char('Drawing Description',readonly=True)
    submitted_by = fields.Many2one('res.users', 'Submitted By',readonly=True)
    submitted_date = fields.Date('Submitted Date',readonly=True)
    rev0 = fields.Date("Rev0", readonly=True)
    rev1 = fields.Date("Rev1", readonly=True)
    rev2 = fields.Date("Rev2", readonly=True)
    rev3 = fields.Date("Rev3", readonly=True)
    rev4 = fields.Date("Rev4", readonly=True)
    rev5 = fields.Date("Rev5", readonly=True)
    rev6 = fields.Date("Rev6", readonly=True)
    bbs_weight = fields.Float(string="BBS Qty",readonly=True)
    delivered_qty = fields.Float(string="Delivered Qty", readonly=True)
    balance_qty = fields.Float(string="Balance Qty", readonly=True)

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, 'tech_drawing_register')
        self.env.cr.execute("""
            create or replace view tech_drawing_register as (

             WITH dwg_register AS (
 SELECT s.id, max(s.id) AS submittal_id, max(r.submittal_date) AS submitted_date , max(r.id) AS revision_id,
            max(
                CASE
                    WHEN r.revision_number = 0 THEN r.submittal_date
                    ELSE NULL::date
                END) AS rev0,
            max(
                CASE
                    WHEN r.revision_number = 1 THEN r.submittal_date
                    ELSE NULL::date
                END) AS rev1,
            max(
                CASE
                    WHEN r.revision_number = 2 THEN r.submittal_date
                    ELSE NULL::date
                END) AS rev2,
            max(
                CASE
                    WHEN r.revision_number = 3 THEN r.submittal_date
                    ELSE NULL::date
                END) AS rev3,
            max(
                CASE
                    WHEN r.revision_number = 4 THEN r.submittal_date
                    ELSE NULL::date
                END) AS rev4,
            max(
                CASE
                    WHEN r.revision_number = 5 THEN r.submittal_date
                    ELSE NULL::date
                END) AS rev5,
            max(
                CASE
                    WHEN r.revision_number = 6 THEN r.submittal_date
                    ELSE NULL::date
                END) AS rev6
           FROM tech_submittal s
      INNER JOIN tech_submittal_revision r ON r.submittal_id = s.id
      WHERE r.state NOT IN ('cancel')
     GROUP BY s.id
),
_dwg_reg AS (

 SELECT dwg.id,rev.submitted_by, dwg.submittal_id, dwg.revision_id, dwg.submitted_date,  dwg.rev0, dwg.rev1,
            dwg.rev2, dwg.rev3, dwg.rev4, dwg.rev5, dwg.rev6,
            string_agg(d.name::text, '
'::text ORDER BY d.name::text) AS drawing,
            string_agg(dr.description::text, '
'::text ORDER BY d.name) AS description,
            max(rev.bbs_weight) AS bbs_weight
           FROM dwg_register dwg
           INNER JOIN tech_submittal_document_revision dr ON dwg.revision_id = dr.revision_id
      INNER  JOIN tech_submittal_revision_document d ON dr.document_id = d.id

   LEFT JOIN tech_submittal_revision rev ON dwg.revision_id = rev.id
  GROUP BY dwg.id, rev.submitted_by, dwg.submittal_id, dwg.revision_id,dwg.submitted_date, dwg.rev0, dwg.rev1, dwg.rev2, dwg.rev3, dwg.rev4, dwg.rev5, dwg.rev6
  ORDER BY dwg.id


)

SELECT _dwg_reg.id,_dwg_reg.submitted_by, sub.job_site_id, _dwg_reg.submittal_id,
    _dwg_reg.revision_id,  _dwg_reg.submitted_date ,_dwg_reg.rev0, _dwg_reg.rev1, _dwg_reg.rev2,
    _dwg_reg.rev3, _dwg_reg.rev4, _dwg_reg.rev5, _dwg_reg.rev6,
    _dwg_reg.drawing AS name, _dwg_reg.description,
    max(_dwg_reg.bbs_weight) AS bbs_weight,
    sum(del.delivered_qty) AS delivered_qty,
    max(_dwg_reg.bbs_weight) - sum(del.delivered_qty) AS balance_qty
   FROM _dwg_reg
   LEFT JOIN tech_delivery_details del ON del.revision_id = _dwg_reg.revision_id
   LEFT JOIN tech_submittal sub ON _dwg_reg.submittal_id = sub.id
  GROUP BY _dwg_reg.id, _dwg_reg.submitted_by ,sub.job_site_id, _dwg_reg.submittal_id, _dwg_reg.revision_id,_dwg_reg.submitted_date, _dwg_reg.rev0, _dwg_reg.rev1, _dwg_reg.rev2, _dwg_reg.rev3, _dwg_reg.rev4, _dwg_reg.rev5, _dwg_reg.rev6, _dwg_reg.drawing, _dwg_reg.description

  ORDER BY _dwg_reg.id


            )
        """)

DrawingRegister()
