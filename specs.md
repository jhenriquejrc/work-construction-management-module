### Escopo funcional e técnico — Módulo Odoo v19.0: Gerenciamento de Obras em Condomínios

**Nome sugerido para o menu do portal:** **Minhas Unidades** (alternativas: *Meus Lotes*, *Minhas Propriedades*).  
**Nome do módulo:** `condominio_obras` (ou `condo_construction`).

---

## Visão geral
- Portal: usuário (morador/proprietário) acessa **Minhas Unidades** e cria/seleciona uma **Unidade/Lote** (campos: *Lote*, *Quadra*, *Proprietário*).  
- Demanda: usuário cria uma **Obra** vinculada à unidade, seleciona **Tipo de Demanda** (BackOffice cadastra tipos; inicialmente **Construção**).  
- Cada **Tipo de Demanda** define um conjunto de **Documentos obrigatórios** (título, descrição, flag *requerido*).  
- Usuário anexa documentos; cada arquivo pode ser **Aprovado** ou **Reprovado** por um analista com justificativa.  
- Workflow por estágios (kanban/lista): **Aguardando análise**, **Em análise**, **Aguardando Cliente**, **Aprovado**, **Reprovado**.  
- Notificações via chatter/email quando analista aprova/reprova; histórico de versões de documentos.  
- Permissões: portal para proprietários; backoffice para analistas/gestores.

---

## Modelos (principais)
- `condo.property` — **Unidade / Lote**
  - `name` (char) — ex: "Lote 12 - Quadra B"
  - `lote` (char), `quadra` (char)
  - `owner_id` (many2one res.partner)
  - `user_id` (many2one res.users) — vinculado ao portal user
  - `work_ids` (one2many condo.work)

- `condo.work.type` — **Tipo de Demanda**
  - `name` (char) — ex: "Construção"
  - `document_template_ids` (one2many condo.work.type.document)

- `condo.work.type.document` — **Documento exigido por tipo**
  - `work_type_id` (many2one)
  - `title` (char)
  - `description` (text)
  - `required` (boolean)

- `condo.work` — **Obra / Demanda**
  - `name` (char, sequence)
  - `property_id` (many2one condo.property)
  - `type_id` (many2one condo.work.type)
  - `stage_id` (many2one condo.work.stage)
  - `state` (selection) — redundante com stage para filtros rápidos
  - `document_ids` (one2many condo.work.document)
  - `analyst_id` (many2one res.users)
  - `date_submitted`, `date_closed`
  - chatter (mail.thread)

- `condo.work.document` — **Documento enviado**
  - `work_id` (many2one)
  - `title` (char)
  - `description` (text)
  - `attachment_id` (many2one ir.attachment) or `datas` binary
  - `upload_user_id` (many2one res.users)
  - `upload_date`
  - `review_state` (selection: `pending`, `approved`, `rejected`)
  - `reviewer_id` (many2one res.users)
  - `review_comment` (text)
  - `review_date`

- `condo.work.stage` — **Estágios Kanban**
  - `name` (char)
  - `sequence` (int)
  - `fold` (boolean)

---

## Regras de negócio / Workflow
- Ao criar obra no portal, **todos** os documentos marcados como `required` para o tipo aparecem como campos para upload; o usuário pode enviar todos ou alguns (validação no submit).
- **Submissão**: usuário clica "Submeter para Análise" — obra passa para estágio **Aguardando análise** e notifica analistas (grupo BackOffice).
- **Análise**: analista abre obra, revisa documentos individualmente e define `review_state` e `review_comment`.  
  - Se **todos** documentos aprovados → obra para estágio **Aprovado**.  
  - Se **algum** documento reprovado → obra para estágio **Aguardando Cliente**; notifica usuário com justificativas por documento.  
  - Analista pode marcar obra **Em análise** enquanto revisa.
- Usuário corrige e reenvia documentos; histórico de versões mantido (nova attachment ou substituição com versão).
- Possibilidade de **reprovação final** (estágio **Reprovado**) caso não atenda regras administrativas.

---

## Portal (UX)
- Menu no portal: **Minhas Unidades** → lista de unidades do usuário.  
- Dentro da unidade: botão **Nova Obra** → formulário com seleção de *Tipo de Demanda* e upload dos documentos obrigatórios (cada documento com título/descrição e campo de arquivo).  
- Visualização da obra: timeline (chatter), lista de documentos com status (pendente/aprovado/reprovado) e comentários do analista.  
- Ações: *Submeter*, *Retificar documentos*, *Cancelar*.

---

## Views e UI (exemplos)
- **Kanban** e **Tree** para `condo.work` com `stage_id` como coluna do kanban.  
- **Form** para `condo.work` com notebook: Dados da obra | Documentos (one2many) | Histórico/Chatter.  
- **Form portal** simplificado com upload inline e validação JS para obrigatoriedade.

---

## Segurança e Acessos
- Grupos:
  - `group_condo_portal` — portal users (acesso apenas às suas unidades e obras).
  - `group_condo_analyst` — analistas (BackOffice) com permissão para aprovar/reprovar.
  - `group_condo_manager` — gestores (acesso total).
- Regras de registro (record rules):
  - Portal: `['|', ('user_id', '=', user.id), ('owner_id.user_id', '=', user.id)]` para `condo.property` e `condo.work`.
  - Analistas: acesso a todas obras do condomínio.
- ACLs (ir.model.access.csv) para cada modelo com CRUD apropriado.

---

## Integrações e notificações
- **Mail templates**:
  - Notificar analistas quando obra é submetida.
  - Notificar usuário quando documento é reprovado (incluir justificativa).
  - Notificar quando obra é aprovada/reprovada.
- **Automated actions / Server actions**:
  - Atualizar `stage_id` automaticamente quando todos documentos aprovados.
- **Chatter**: registrar cada revisão de documento como mensagem com anexo.

---

## Dados iniciais (demo)
- Carregar estágios padrão (`condo.work.stage`): *Aguardando análise*, *Em análise*, *Aguardando Cliente*, *Aprovado*, *Reprovado*.
- Criar `condo.work.type` inicial: **Construção** com documentos obrigatórios (ex.: *Projeto Arquitetônico*, *Alvará*, *ART/CREA*).

---

## Exemplo de código (esqueleto) — Python (models)
```python
# models/condo_property.py
from odoo import models, fields, api

class CondoProperty(models.Model):
    _name = 'condo.property'
    _description = 'Unidade / Lote'

    name = fields.Char(required=True)
    lote = fields.Char()
    quadra = fields.Char()
    owner_id = fields.Many2one('res.partner', string='Proprietário')
    user_id = fields.Many2one('res.users', string='Portal User')
    work_ids = fields.One2many('condo.work', 'property_id', string='Obras')
