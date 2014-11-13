# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2008 Alfatek All Rights Reserved
#                    Dorin Hongu <dhongu(@)gmail(.)com       
#
##############################################################################

from openerp.osv import fields, osv
import time
import datetime
from openerp import tools
import openerp.addons.decimal_precision as dp
"""

Data    Ora    Tip tranzactie    Număr Inmatriculare        Tip combustibil    Cantitate        Pret / litru    Total valoare    Statia    Cod dispozitiv    Kilometri    Număr factura    Nume Flota
18.02.2013    10:10    Statii Rompetrol    B60WZJ        EFIX BENZINA 95     43,00        6,11    262,73    BACAU 2    8012012079740002401    0        ROMCHIM PROTECT SA
17.02.2013    14:21    Statii Rompetrol    B17RCH        EFIX MOTORINA 51 WINTER     20,19        6,17    124,57    BUZAU 1    8012012079740017404    0        ROMCHIM PROTECT SA
17.02.2013    08:31    Statii Rompetrol    B30RCH        EFIX BENZINA 95     54,93        6,11    335,62    BACAU 2    8012012079740020409    0        ROMCHIM PROTECT SA
16.02.2013    15:01    Statii Rompetrol    ROMCHM1         EFIX MOTORINA 51 WINTER     60,51        6,15    372,14    PIATRA NEAMT 1    8012012079740015406    0        ROMCHIM PROTECT SA
16.02.2013    13:15    Statii Rompetrol    B60WZJ        EFIX BENZINA 95     29,95        6,11    182,99    BACAU 2    8012012079740002401    0        ROMCHIM PROTECT SA
"""




class fleet_fillandgo(osv.osv_memory):
    _name = 'fleet.fillandgo'
    _description = 'Fill and go'
    _columns = {
        'date':          fields.datetime('Data'),
        'license_plate': fields.char('License Plate', size=32),
        'vehicle_id':    fields.many2one('fleet.vehicle', 'Vehicle'),
        'fule_id':       fields.many2one('fleet.fuel', 'Fule'),
        'liter':         fields.float('Liter'),
        'price_per_liter': fields.float('Price Per Liter'),
        'amount':        fields.float('Total Price'), 
        'station_id':    fields.many2one('fleet.location', 'Station'), # de daugat domeniul
        'card_id':       fields.many2one('fleet.card', 'Card'),
        'odometer':      fields.float('Odometer Value'),
        'inv_ref':       fields.char('Invoice Reference', size=64),
    }
    
fleet_fillandgo()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: