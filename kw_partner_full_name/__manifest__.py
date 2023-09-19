{
    'name': 'Contacts full name',

    'author': 'Kitworks Systems',
    'website': 'https://kitworks.systems/',

    'category': 'Extra Tools',
    'license': 'OPL-1',
    'version': '14.0.0.0.2',
    'depends': [
        'base',
    ],
    'data': [
        'views/partner_view.xml',
    ],
    'installable': True,

    'post_init_hook': 'kw_put_names_to_firstname',

    'images': [
        'static/description/cover.png',
        'static/description/icon.png',
    ],
}
