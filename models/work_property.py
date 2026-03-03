from odoo import models, fields, api


class WorkProperty(models.Model):
    _name = 'work.property'
    _description = 'Work Property'
    _rec_name = 'name'
    _order = 'name'

    name = fields.Char(string='Property Name', required=True, index=True)
    description = fields.Text(string='Description')
    active = fields.Boolean(string='Active', default=True)
    lot_number = fields.Char(string='Lot Number')
    address = fields.Char(string='Address')
    owner_id = fields.Many2one('res.partner', string='Owner')
    user_id = fields.Many2one('res.users', string='Responsible User')
    work_ids = fields.One2many('work.management', 'property_id', string='Works')
    
