from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class WorkManagement(models.Model):
    _name = 'work.management'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Obra / Demanda'

    name = fields.Char(string='Número', required=True, copy=False, default=lambda self: _('New'))
    property_id = fields.Many2one('work.property', string='Propriedade', required=True)
    stage_id = fields.Many2one(
        'work.stage',
        string='Estágio',
        required=True,
        default=lambda self: self._default_stage_id(),
        group_expand='_group_expand_stage_id',
        tracking=True,
    )
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
    def _default_stage_id(self):
        stage = self.env.ref('work_construction_management.stage_awaiting_analysis', raise_if_not_found=False)
        if stage:
            return stage.id
        return self.env['work.stage'].search([], order='sequence, name', limit=1).id

    @api.model
    def _group_expand_stage_id(self, stages, domain, order=None, **kwargs):
        return self.env['work.stage'].search([], order='sequence, name')

    def _set_stage_and_state(self, stage_xml_id, state):
        for rec in self:
            rec.stage_id = self.env.ref(stage_xml_id).id
            rec.state = state

    def _ensure_required_documents(self):
        for rec in self:
            if not rec.work_type_id:
                continue
            for doc_type in rec.work_type_id.work_document_type_ids:
                existing = rec.document_ids.filtered(lambda d: d.document_type_id == doc_type)
                if existing:
                    continue
                self.env['work.document'].create({
                    'work_id': rec.id,
                    'document_type_id': doc_type.id,
                    'title': doc_type.name,
                    'description': doc_type.description,
                })

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            seq = self.env['ir.sequence'].sudo().next_by_code('work.management') or _('New')
            vals['name'] = seq
        record = super().create(vals)
        record._ensure_required_documents()
        return record

    def action_submit(self):
        for rec in self:
            # valida documentos obrigatórios
            required_docs = rec.work_type_id.work_document_type_ids.filtered(lambda d: d.required)
            missing = []
            for d in required_docs:
                if not rec.document_ids.filtered(lambda x: x.document_type_id == d and x.attachment_id):
                    missing.append(d.name)
            if missing:
                raise ValidationError(_('Documentos obrigatórios faltando: %s') % ', '.join(missing))
            rec.date_submitted = fields.Datetime.now()
            rec._set_stage_and_state('work_construction_management.stage_awaiting_analysis', 'submitted')
            # notificar analistas (ex: enviar email ou criar atividade)

    def action_mark_in_progress(self):
        self._set_stage_and_state('work_construction_management.stage_in_analysis', 'in_progress')

    def action_wait_client(self):
        self._set_stage_and_state('work_construction_management.stage_awaiting_client', 'submitted')

    def action_approve(self):
        self._set_stage_and_state('work_construction_management.stage_approved', 'approved')

    def action_reject(self):
        self._set_stage_and_state('work_construction_management.stage_rejected', 'rejected')
