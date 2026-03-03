from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class WorkManagement(models.Model):
    _name = 'work.management'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Obra / Demanda'

    name = fields.Char(string='Número', required=True, copy=False, default=lambda self: _('New'))
    property_id = fields.Many2one('work.property', string='Propriedade', required=True)
    stage_id = fields.Many2one('work.stage', string='Estágio', tracking=True)
    work_type_id = fields.Many2one('work.type', string='Tipo de Demanda')
    document_ids = fields.One2many('work.document', 'work_id', string='Documentos')
    analyst_id = fields.Many2one('res.users', string='Analista')
    date_submitted = fields.Datetime()
    state = fields.Selection([
        ('draft','Rascunho'),
        ('submitted','Enviado '),
        ('in_progress','Em análise'),
        ('approved','Aprovado'),
        ('rejected','Reprovado'),
    ], default='draft', tracking=True)

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            seq = self.env['ir.sequence'].next_by_code('work.management') or _('New')
            vals['name'] = seq
        return super().create(vals)

    def action_submit(self):
        for rec in self:
            # valida documentos obrigatórios
            required_docs = rec.type_id.document_template_ids.filtered(lambda d: d.required)
            missing = []
            for d in required_docs:
                if not rec.document_ids.filtered(lambda x: x.title == d.title and x.attachment_id):
                    missing.append(d.title)
            if missing:
                raise ValidationError(_('Documentos obrigatórios faltando: %s') % ', '.join(missing))
            rec.state = 'submitted'
            rec.date_submitted = fields.Datetime.now()
            rec.stage_id = self.env.ref('work_construction_management.stage_awaiting_analysis').id
            # notificar analistas (ex: enviar email ou criar atividade)
