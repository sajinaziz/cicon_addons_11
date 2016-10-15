from odoo import models, fields, api


class CmmsSparePartTypeWizard(models.TransientModel):
    _name = 'cmms.spare.part.type.wizard'
    _description = "Spare Part Type"

    part_type_id = fields.Many2one('cmms.spare.part.type', string="Spare Part Type", required=True)

    @api.multi
    def assign_type(self):
        self.ensure_one()
        if self._context.get('invoice_line_ids',False):
            _line = self.env['cmms.store.invoice.line'].search([('id', 'in', self._context.get('invoice_line_ids'))])
            _line.write({'spare_part_type_id': self.part_type_id.id})
        return True

CmmsSparePartTypeWizard()