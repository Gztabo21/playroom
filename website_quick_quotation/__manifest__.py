# -*- coding: utf-8 -*-
#################################################################################
# Author      : CFIS (<https://www.cfis.store/>)
# Copyright(c): 2017-Present CFIS.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://www.cfis.store/>
#################################################################################

{
    "name": "Quick quotation | Website quick quotation | Quick Quotation Request Create from Website",
    "summary": """
        This module allows your clients and website visitors to generate quotations by filling out a products form from website and submitting it.
        """,
    "version": "14.0.1",
    "description": """
        This module allows your clients and website visitors to generate quotations by filling out a products form from website and submitting it.
        """,    
    "author": "CFIS",
    "maintainer": "CFIS",
    "license" :  "Other proprietary",
    "website": "https://www.cfis.store",
    "images": ["images/website_quick_quotation.png"],
    "category": "website",
    "depends": [
        "base",        
        "sale_management",
        "website",
    ],
    "data": [
        "data/website_data.xml",
        "views/assets.xml",
    ],
    "installable": True,
    "application": True,
    "price"                 :  55,
    "currency"              :  "EUR",
    "pre_init_hook"         :  "pre_init_check",
}