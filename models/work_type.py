from odoo import models, fields


class WorkType(models.Model):
    _name = 'work.type'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Work Type'
    _rec_name = 'name'
    _order = 'name'

    name = fields.Char(string='Type Name', required=True)
    description = fields.Text(string='Description')
    active = fields.Boolean(string='Active', default=True)
    work_document_type_ids = fields.Many2many('work.document.type', string='Document Templates')
