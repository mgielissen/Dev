# -*- coding: utf-8 -*-
{
    'name': "aa_houbolak",

    'summary': """
        Customization of Ecommerce adding new fields at cart update""",

    'description': """
        Customization for Yenth specifications...
        1) Customer opens shop and clicks on 'shop'
         => he first has to choose a selection type from the dropdown finishing
        2) The user clicks on the button 'Bevestigen' and gets redirected to
         /shop where only products are shown that match the selected finishing.
        3) The user can select products and add them to the cart and add the
         extra things that need to be filled in on the products page
        4) Extra page to select color.
    """,
    'author': "Jeremy Kersten",
    'category': 'Sales',
    'version': '0.2',
    'depends': ['website_sale'],
    'data': [
        'security/ir.model.access.csv',
        'templates.xml',
    ],
}
