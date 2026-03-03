from odoo import models, fields


class WorkDocumentType(models.Model):
    _name = 'work.document.type'
    _description = 'Work Document Type'
    _rec_name = 'name'
    _order = 'date desc, name'

    name = fields.Char(string='Document Name', required=True)
    description = fields.Text(string='Description')
    date = fields.Date(string='Document Date', default=fields.Date.today)
    active = fields.Boolean(string='Active', default=True)
