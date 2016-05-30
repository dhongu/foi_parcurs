# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2008 Deltatech All Rights Reserved
#                    Dorin Hongu <dhongu(@)gmail(.)com       
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    "name" : "Alfatek Fleet",
    "version" : "1.0",
    "author" : "Dorin Hongu",
    "category" : "Managing vehicles and contracts",
    'summary' : 'Vehicle, route, map sheet',
    "depends" : ["fleet"],
    "description" : """
Extension for Fleet Application
==================================
Acest modul este o extensie a aplicatiei de gestiune parc auto.

Main Features
-------------
* Campuri suplimentare in  detele de baza ale unui vehicul.
        * indicativ
        * sofer de rezerva
        * categorie
        * nivel rezervor
        * capacitate rezervor
        * consum mediu
        * viteza medie
        * carduri de alimentare
* Gestionare carduri de alimentare
* Gestionare trasee
        * gestionare locatii
        * gestionare distante intre locatii si durate de deplasare
* Gestionare foi de parcurs
        * trasee aferente unei foi de parcusrs
        * carburant
* Calculare automata a nivelului de carburant din rezervor

Nota
Campul data din fleet trebuie modificat in datatime


    """,
    "data" : [
            "fleet_data.xml",
            "fleet_view.xml",
            "fleet_report.xml",
            "views/report_map_sheet.xml",
            'security/ir.model.access.csv'
    ],
    

    "active": False,
    "installable": True,
   
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
