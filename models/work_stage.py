from odoo import models, fields


class WorkStage(models.Model):
    _name = 'work.stage'
    _description = 'Work Stage'
    _rec_name = 'name'
    _order = 'sequence, name'

    name = fields.Char(string='Stage Name', required=True)
    description = fields.Text(string='Description')
    sequence = fields.Integer(string='Sequence', default=10)
    active = fields.Boolean(string='Active', default=True)
