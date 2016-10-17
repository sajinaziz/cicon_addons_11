from odoo import models, fields, tools, api


class cicon_order_analysis_report(models.Model):
    _name = 'cicon.order.analysis.report'
    _description = "Order Analysis Report"
    _auto = False
    _rec_name = 'product_id'

    partner_id = fields.Many2one('res.partner', "Customer", readonly=True)
    #project_id = fields.Many2one('res.partner.project', "Project", readonly=True)
    project_id = fields.Many2one('cicon.job.site', "Project", readonly=True)
    product_id = fields.Many2one('product.product', "Product", readonly=True)
    product_tmpl_id = fields.Many2one('product.template', "Template", readonly=True)
    categ_id = fields.Many2one('product.category', "Category", readonly=True)
    dia_attrib_value_id = fields.Many2one('product.attribute.value', "Dia Value", readonly=True)
    prod_order_id = fields.Many2one('cicon.prod.order', "Production Order", readonly=True)
    quantity = fields.Float('Quantity', decimal=(10, 3), readonly=True)
    state = fields.Char("State", readonly=True)

    def _from(self):
        from_str = """cicon_prod_order_line AS L INNER JOIN
     cicon_prod_order AS O ON L.prod_order_id = O.id INNER JOIN
     cicon_customer_order AS C ON O.customer_order_id = C.id INNER JOIN
     product_product AS P ON L.product_id = P.id INNER JOIN
     product_template AS T ON P.product_tmpl_id = T.id
     """
        return from_str

    def _select(self):
        select_str = """SELECT
              MIN(L.id) AS id,
              C.partner_id,
              C.project_id,
              L.prod_order_id,
              L.product_id,
              L.dia_attrib_value_id,
              T.categ_id,
              P.product_tmpl_id,
              O.state,
              SUM(L.product_qty) AS quantity
              """
        return select_str


    def _group_by(self):
        group_by_str = """
    GROUP BY
      C.partner_id,
      C.project_id,
      L.prod_order_id,
      L.product_id,
      L.dia_attrib_value_id,
      T.categ_id,
      P.product_tmpl_id,
      O.state
      """
        return group_by_str

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr,self._table)
        self.env.cr.execute("""CREATE or REPLACE VIEW %s as (
            %s
            FROM ( %s )
            %s
            )""" % (self._table, self._select(), self._from(), self._group_by()))


cicon_order_analysis_report()







