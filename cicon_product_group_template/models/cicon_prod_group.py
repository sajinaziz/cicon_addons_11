from odoo import models, fields, api


class cicon_product_group_template(models.Model):
    _name = 'cicon.product.group.template'
    _description = "CICON Product Group template"




    @api.onchange('template_ids')
    def _get_products(self):
        _dm = {'product_ids': ''}
        if self.template_ids:
            _dm = {'product_ids': [('product_tmpl_id', 'in', self.template_ids.ids)]}
        return {'domain': _dm}


    name = fields.Char("Group Template Name", required=True)
    code = fields.Char('Group Code')
    description = fields.Char('Description')
    unit_id = fields.Many2one('product.uom',  string='Unit', required=True)
    template_ids = fields.Many2many('product.template', 'cicon_product_group_tmpl_rel', 'product_tmpl_group_id', 'template_id', string="Templates")
    product_ids = fields.Many2many('product.product', 'cicon_product_group_prod_rel', 'product_tmpl_group_id', 'product_id',string="Templates")
    attributes_ids = fields.One2many('cicon.product.group.attribute','prodcut_group_tmpl_id', string="Product Group Template")

    _sql_constraints = [('uniq_name', 'UNIQUE(name)', 'Name Should be Unique'),
                        ('uniq_code', 'UNIQUE(code)', 'Code Should be Unique')]

    @api.one
    def copy(self, default=None):
        if default is None:
            default = {}
        if not default.get('name', False):
            default.update(name=('%s/Copy') % (self.name))
        #default.update(state='pending')
        return super(cicon_product_group_template, self).copy(default)


cicon_product_group_template()

class cicon_product_group_attribute(models.Model):
    _name = 'cicon.product.group.attribute'
    _description = "CICON Product Group Attribute"

    prodcut_group_tmpl_id = fields.Many2one('cicon.product.group.template', "Product Group Template")
    attribute_id = fields.Many2one('product.attribute', string="Product Attribute")
    attr_value_ids = fields.Many2many('product.attribute.value', 'cicon_prd_grp_attr_val_rel', string="Product Attribute Value")

cicon_product_group_attribute()




