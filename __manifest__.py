{
    'name': 'Work Construction Management',
    'version': '18.0.1.0.0',
    'summary': 'Module for managing construction projects, including stages, lots, and documents.',
    'category': 'Project',
    'author': 'Datasheep, Joao Henrique',
    'depends': ['base', 'portal', 'website'],
    'data': [
        'security/ir.model.access.csv',
        'data/work_stage.xml',
        'data/work_actions.xml',
        'views/work_management_kanban_views.xml',
        'views/work_stage_views.xml',
        'views/work_property_views.xml',
        'views/work_document_views.xml',
        'data/menu_views.xml',
    ],
    'application': True,
}