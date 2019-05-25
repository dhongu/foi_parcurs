# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2015 Deltatech All Rights Reserved
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



from openerp.exceptions import except_orm, Warning, RedirectWarning, ValidationError 
from openerp import models, fields, api, _
from openerp import SUPERUSER_ID, api
import openerp.addons.decimal_precision as dp
 

class fleet_vehicle(models.Model):
    _inherit = 'fleet.vehicle'
    
    id_gps = fields.Char(string="ID GPS Tracker")
    on_line = fields.Boolean(string="GPS Online", readonly=True)
    processing_date = fields.Datetime(string="Processing Time", readonly=True)
    gps_date   =   fields.Datetime(string='GPS Date', readonly=True)
    lat        =   fields.Float(string='Latitude', digits=(9, 6), readonly=True)
    lng        =   fields.Float(string='Longitude', digits=(9, 6), readonly=True)
    nmea_protocol = fields.Selection([('Meiligao','Meiligao'),('Meitrack','Meitrack'),('VT310BB','VT310BB')], string="Protocol NMEA", readonly=True)
     

class fleet_gps_point(models.Model):
    _name = 'fleet.gps.point'
    _description = 'Fleet GPS Point'
    
    vehicle_id =   fields.Many2one('fleet.vehicle', string='Vehicle', index=True)
    date       =   fields.Datetime(string='Date', index=True)
    lat        =   fields.Float(string='Latitude', digits=(9, 6))
    lng        =   fields.Float(string='Longitude', digits=(9, 6))
    speed      =   fields.Float(string='Speed', digits=(4, 1))     
    crs        =   fields.Float(string='Crs', digits=(4, 1))  
    hdop       =   fields.Float(string='HDOP', digits=(5, 1))  
    input      =   fields.Integer(string='Input')  
    output     =   fields.Integer(string='Output') 
    ad1        =   fields.Integer(string='AD1') 
    ad2        =   fields.Integer(string='AD2') 
    alarm      =   fields.Char(string='Alarm')
         

class fleet_gps_route(models.Model):
    _name = 'fleet.gps.route'
    _description = 'Fleet GPS Route'
    
    vehicle_id =   fields.Many2one('fleet.vehicle', string='Vehicle', index=True)
    date_begin = fields.Datetime(string='Date Begin', index=True)
    date_end   =   fields.Datetime(string='Date End', index=True)
    from_date   = fields.Date(string='Date')
    lat_init        =   fields.Float(string='Latitude initial', digits=(9, 6))
    lng_init       =   fields.Float(string='Longitude initial', digits=(9, 6))
    lat_fin        =   fields.Float(string='Latitude final', digits=(9, 6))
    lng_fin        =   fields.Float(string='Longitude final', digits=(9, 6))    
    
    from_loc_id = fields.Many2one('fleet.location', string='From', help='From location', required=True)
    to_loc_id   = fields.Many2one('fleet.location', string='To',   help='To location',   required=True)     

