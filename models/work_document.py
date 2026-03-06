from odoo import models, fields


class WorkDocument(models.Model):
    _name = 'work.document'
    _description = 'Work Document'
    _rec_name = 'title'
    _order = 'upload_date desc, title'

    work_id = fields.Many2one('work.management', string='Work', required=True)
    document_type_id = fields.Many2one('work.document.type', string='Document Type')
    title = fields.Char(string='Document Name', required=True)
    description = fields.Text(string='Description')
    attachment_id = fields.Many2one('ir.attachment', string='Attachment')
    upload_user_id = fields.Many2one('res.users', string='Uploaded By', default=lambda self: self.env.user.id)
    upload_date = fields.Datetime(string='Upload Date', default=fields.Datetime.now)
    review_status = fields.Selection([
        ('pending', 'Pendente'),
        ('approved', 'Aprovado'),
        ('rejected', 'Rejeitado'),
    ], string='Review Status', default='pending', tracking=True)
    reviewer_id = fields.Many2one('res.users', string='Reviewer')
    review_comment = fields.Text(string='Review Comment')
    review_date = fields.Datetime(string='Review Date')

