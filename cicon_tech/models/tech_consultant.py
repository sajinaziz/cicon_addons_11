from odoo import models, fields, api

class TechConsultant(models.Model):

    _name = 'tech.consultant'
    _description = "Consultant Details"


    name = fields.Char('Name', size=250, required=True, help="Consultant Name")
    designation = fields.Char('Designation', size=150)
    email = fields.Char('Email', size=250, help="Consultant Email ID")
    phone_num = fields.Char('Telephone', size=50)

TechConsultant()
