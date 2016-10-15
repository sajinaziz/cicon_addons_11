from odoo import models, fields, api

# is to store equipment category property name

class HrEquipmentCategoryProperty(models.Model):
    _name = 'hr.equipment.category.property'
    _description = "Equipment Category Property"

    #store the property name
    name = fields.Char('Property Name', required=True)

    # set property name field as unique key constraint
    _sql_constraints = [('uniq_name', 'UNIQUE(name)', "Property Name Should be Unique" )]

HrEquipmentCategoryProperty()

#is to store the equipment current status
class HrEquipmentStatus(models.Model):
    _name = 'hr.equipment.status'
    _description = "Equipment Status"

    #store the status
    name = fields.Char('Status', required=True)
    sequence=fields.Integer('Sequence')

    _order = 'sequence'

    # set status field as unique key constraint
    _sql_constraints = [('uniq_name', 'UNIQUE(name)', "Status should be Unique")]

HrEquipmentStatus()

# store the equipment property value details
class HrEquipmentPropertyValue(models.Model):
    _name = 'hr.equipment.property.value'
    _description = "Equipment Category Property"

    #store equipment id , relate to equipment table
    equipment_id = fields.Many2one('hr.equipment', string="Equipment")
    #store property id, relate to equipment category property
    property_id = fields.Many2one('hr.equipment.category.property', "Property")
    # store property value
    property_value = fields.Char('Value', required=True)

    # add unique constraint  to equipment id and property id
    _sql_constraints = [('uniq_name', 'UNIQUE(equipment_id,property_id)', "Property Should be Unique")]

HrEquipmentCategoryProperty()

#store equipment related data
class HrEquipment(models.Model):
    _inherit = 'hr.equipment'

    # generate asset code using function. Take the values of name and serial no.,
    #  then combine these two fields and generate asset code.

    @api.one
    @api.depends('name', 'serial_no')
    def _get_asset_name(self):
        if self.name:
            self.asset_code = str(self.name)
            if self.serial_no:
                self.asset_code += '/' + str(self.serial_no)

    #take the default status of the equipment
    def _get_default_status(self):
        _status = self.env['hr.equipment.status'].search([], order='sequence desc', limit=1)
        return _status

    #create a many2many relation nd store property ids
    property_ids = fields.Many2many(related='category_id.property_ids', store=False, string="Properties")
    #property_value_ids, create a relation to equipment property value table and store property values
    property_value_ids = fields.One2many('hr.equipment.property.value', 'equipment_id', string="Property Values")
    #company_id, relate to company table and store company,then set the current logged user company as the default company
    company_id = fields.Many2one('res.company', "Company", default=lambda self: self.env.user.company_id, track_visibility='onchange')
    #store asset code
    asset_code = fields.Char(compute=_get_asset_name, string="Asset Code", store=True)
    #store the equipment staus
    status_id = fields.Many2one('hr.equipment.status', string='Status', track_visibility='onchange', default=_get_default_status)

    employee_id = fields.Many2one('hr.employee', string='Employee')
    department_id = fields.Many2one('hr.department', string='Department', related='employee_id.department_id')

    #Add unique constaint to asset code
    _sql_constraints = [('UniqueAsset', 'UNIQUE(asset_code)', 'Asset Name Should be Unique !')]

HrEquipment()

# to store equipment request categories
class HrEquipmentRequestCategory(models.Model):
    _name = 'hr.equipment.request.category'
    _description = "Request Category"

    #store the request category name
    name = fields.Char('Category', required=True)
    #asset_categ_ids, create a manytomany relation to equipment category table and store asset_categ_ids
    asset_categ_ids = fields.Many2many('hr.equipment.category', 'hr_equip_categ_req_categ_rel',
                                    'req_categ_id', "asset_categ_id", string="Asset Categories")
    #parent id, set the main parent id
    parent_id = fields.Many2one('hr.equipment.request.category', string="Parent")
    #child_ids, create a one to many relation to equipment request category and store child ids
    child_ids = fields.One2many('hr.equipment.request.category', 'parent_id', string='Children Categories')
    #store the required information details to solve the issues
    note = fields.Text(string='Required Information', help="Required information to solve this category issues, "
                                                           "will apper on description in requests")

    #add unique constraint to name
    _sql_constraints = [('uniq_name', 'UNIQUE(name)', 'Unique Category')]

    @api.multi
    def name_get(self):
        res = []
        for cat in self:
            names = [cat.name]
            pcat = cat.parent_id
            while pcat:
                names.append(pcat.name)
                pcat = pcat.parent_id
            res.append((cat.id, ' / '.join(reversed(names))))
        return res

    @api.one
    @api.constrains
    def _check(self):
        parent = self._parent_name
        # must ignore 'active' flag, ir.rules, etc. => direct SQL query
        query = 'SELECT "%s" FROM "%s" WHERE id = %%s' % (parent, self._table)
        current_id = self.id
        while current_id is not None:
            self._cr.execute(query, (current_id,))
            result = self._cr.fetchone()
            current_id = result[0] if result else None
            if current_id == self.id:
                return False
        return True

HrEquipmentRequestCategory()


#store  the equipment request details
class HrEquipmentRequest(models.Model):
    _inherit = 'hr.equipment.request'

    # company_id, relate to company table and store company,then set the current logged user company as the default company
    company_id = fields.Many2one('res.company', "Company", default=lambda self: self.env.user.company_id)
    #store problem solution
    solution = fields.Text('Solution')
    #request_categ_id, relate to request category table and store request_categ_id
    request_categ_id = fields.Many2one('hr.equipment.request.category',  string="Request Category")
    #request_sub_categ_id, relate to request category table and store request_sub_categ_id
    request_sub_categ_id = fields.Many2one('hr.equipment.request.category', string="Sub Category")
    #ref_no, store maintenance request ref. no.
    ref_no = fields.Char(string="ITMRF No.", default="new")
    department_id = fields.Many2one('hr.department', string='Department', related='employee_id.department_id',track_visibility='onchange')

    @api.onchange('request_sub_categ_id')
    def onchange_request_categ(self):
        if not self.description:
            self.description = self.request_sub_categ_id.note

    @api.model
    def create(self, vals):
        vals['ref_no'] = self.env['ir.sequence'].next_by_code('cicon.maint.internal.seq') or 'New'
        return super(HrEquipmentRequest, self).create(vals)


HrEquipmentRequest()


class HrEquipmentCategory(models.Model):
    _inherit = 'hr.equipment.category'

    property_ids = fields.Many2many('hr.equipment.category.property', 'hr_equipment_categ_property_rel',
                                    'category_id', "property_id", string="Properties")

HrEquipmentCategory()


