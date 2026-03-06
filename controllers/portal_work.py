import base64

from odoo import fields, http, _
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal


class WorkConstructionPortal(CustomerPortal):
	def _prepare_home_portal_values(self, counters):
		values = super()._prepare_home_portal_values(counters)
		if 'work_count' in counters:
			values['work_count'] = request.env['work.management'].search_count(
				self._portal_work_domain()
			)
		return values

	def _portal_work_domain(self):
		user = request.env.user
		return ['|', ('property_id.user_id', '=', user.id), ('property_id.owner_id', '=', user.partner_id.id)]

	def _portal_property_domain(self):
		user = request.env.user
		return ['|', ('user_id', '=', user.id), ('owner_id', '=', user.partner_id.id)]

	def _get_portal_property(self, property_id):
		prop = request.env['work.property'].search(self._portal_property_domain() + [('id', '=', property_id)], limit=1)
		return prop

	def _get_portal_work(self, work_id):
		work = request.env['work.management'].search(self._portal_work_domain() + [('id', '=', work_id)], limit=1)
		return work

	@http.route(['/my/units'], type='http', auth='user', website=True)
	def portal_my_units(self, **kwargs):
		properties = request.env['work.property'].search(self._portal_property_domain(), order='name')
		values = {
			'properties': properties,
			'page_name': 'work_units',
		}
		return request.render('work_construction_management.portal_my_units', values)

	@http.route(['/my/units/create'], type='http', auth='user', website=True, methods=['POST'])
	def portal_create_property(self, **post):
		name = post.get('name')
		lot_number = post.get('lot_number')
		address = post.get('address')
		description = post.get('description')

		if not name:
			values = {
				'properties': request.env['work.property'].search(self._portal_property_domain(), order='name'),
				'page_name': 'work_units',
				'error': _('Property name is required.'),
			}
			return request.render('work_construction_management.portal_my_units', values)

		request.env['work.property'].create({
			'name': name,
			'lot_number': lot_number,
			'address': address,
			'description': description,
			'owner_id': request.env.user.partner_id.id,
			'user_id': request.env.user.id,
		})
		return request.redirect('/my/units')

	@http.route(['/my/units/<int:property_id>/works/new'], type='http', auth='user', website=True)
	def portal_new_work(self, property_id, work_type_id=None, **kwargs):
		prop = self._get_portal_property(property_id)
		if not prop:
			return request.redirect('/my/units')

		work_types = request.env['work.type'].search([('active', '=', True)], order='name')
		selected_type = None
		doc_templates = request.env['work.document.type']
		if work_type_id:
			selected_type = request.env['work.type'].browse(int(work_type_id))
			if selected_type:
				doc_templates = selected_type.work_document_type_ids

		values = {
			'property': prop,
			'work_types': work_types,
			'selected_type': selected_type,
			'doc_templates': doc_templates,
			'page_name': 'work_new',
		}
		return request.render('work_construction_management.portal_new_work', values)

	@http.route(['/my/units/<int:property_id>/works/create'], type='http', auth='user', website=True, methods=['POST'])
	def portal_create_work(self, property_id, **post):
		prop = self._get_portal_property(property_id)
		if not prop:
			return request.redirect('/my/units')

		work_type_id = post.get('work_type_id')
		if not work_type_id:
			return request.redirect('/my/units/%s/works/new' % property_id)

		work = request.env['work.management'].create({
			'property_id': prop.id,
			'work_type_id': int(work_type_id),
		})
		work._ensure_required_documents()
		return request.redirect('/my/works/%s/documents' % work.id)

	@http.route(['/my/works'], type='http', auth='user', website=True)
	def portal_my_works(self, **kwargs):
		works = request.env['work.management'].search(self._portal_work_domain(), order='create_date desc')
		values = {
			'works': works,
			'page_name': 'work_list',
		}
		return request.render('work_construction_management.portal_work_list', values)

	@http.route(['/my/works/<int:work_id>'], type='http', auth='user', website=True)
	def portal_work_detail(self, work_id, **kwargs):
		work = self._get_portal_work(work_id)
		if not work:
			return request.redirect('/my/works')

		values = {
			'work': work,
			'page_name': 'work_detail',
		}
		return request.render('work_construction_management.portal_work_detail', values)

	@http.route(['/my/works/<int:work_id>/documents'], type='http', auth='user', website=True)
	def portal_work_documents(self, work_id, **kwargs):
		work = self._get_portal_work(work_id)
		if not work:
			return request.redirect('/my/works')

		values = {
			'work': work,
			'page_name': 'work_documents',
		}
		return request.render('work_construction_management.portal_work_documents', values)

	@http.route(['/my/works/<int:work_id>/documents/save'], type='http', auth='user', website=True, methods=['POST'])
	def portal_save_documents(self, work_id, **post):
		work = self._get_portal_work(work_id)
		if not work:
			return request.redirect('/my/works')

		for document in work.document_ids:
			input_name = 'doc_%s' % document.id
			file_storage = request.httprequest.files.get(input_name)
			if not file_storage:
				continue
			content = file_storage.read()
			if not content:
				continue

			attachment = request.env['ir.attachment'].sudo().create({
				'name': file_storage.filename,
				'datas': base64.b64encode(content),
				'mimetype': file_storage.mimetype,
				'res_model': 'work.document',
				'res_id': document.id,
			})
			document.write({
				'attachment_id': attachment.id,
				'upload_user_id': request.env.user.id,
				'upload_date': fields.Datetime.now(),
				'review_status': 'pending',
				'review_comment': False,
			})

		if post.get('submit_action') == '1':
			try:
				work.action_submit()
			except Exception as exc:
				values = {
					'work': work,
					'page_name': 'work_documents',
					'error': str(exc),
				}
				return request.render('work_construction_management.portal_work_documents', values)

		return request.redirect('/my/works/%s' % work.id)
