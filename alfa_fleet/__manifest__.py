# -*- coding: utf-8 -*-
# ©  2015-2019 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details
{
    "name": "Alfatek Fleet",
    "version": "1.0",
    "author": "Dorin Hongu",
    "category": "Managing vehicles and contracts",
    'summary': 'Vehicle, route, map sheet',
    "depends": ["fleet"],

    "data": [
        "fleet_data.xml",
        "views/fleet_view.xml",
        "views/fleet_sheet_view.xml",
        "fleet_report.xml",
        "views/report_map_sheet.xml",
        'security/ir.model.access.csv'
    ],

    "active": False,
    "installable": True,

}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
