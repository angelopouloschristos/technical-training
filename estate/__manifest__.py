# -*- coding: utf-8 -*-
{
    'name': "helb_project",
    'summary': """Project for HELB Student""",
    'author': "Patryk Krasucki",
    'website': "http://www.yourcompany.com",
    'category': 'Uncategorized',
    'license': 'LGPL-3',
    'version': '16.0.0.1',
    'depends': ['base', 'sale_management', 'calendar', 'hr'],
    'views': [
        'views/res_partner.xml',
        'views/res_groups.xml',
        'views/sale_order.xml',
        'views/choose_training_date_wizard_form.xml',
    ],
    'data': []
}
