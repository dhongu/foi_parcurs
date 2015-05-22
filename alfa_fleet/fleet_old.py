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


from openerp.exceptions import except_orm, Warning, RedirectWarning
from openerp import models,  api, _
from openerp import SUPERUSER_ID, api
import openerp.addons.decimal_precision as dp





from datetime import datetime, timedelta, date
from openerp.osv import fields, osv
import time
import pytz
from openerp import tools
 
from libxslt import timestamp
import math
 
def str_to_datetime(strdate):
    return  datetime.strptime(strdate, tools.DEFAULT_SERVER_DATETIME_FORMAT)

def datetime_to_str(date_time):
    return  datetime.strftime(date_time, tools.DEFAULT_SERVER_DATETIME_FORMAT)

 

CREATE = lambda values: (0, False, values)
UPDATE = lambda id, values: (1, id, values)
DELETE = lambda id: (2, id, False)
FORGET = lambda id: (3, id, False)
LINK_TO = lambda id: (4, id, False)
DELETE_ALL = lambda: (5, False, False)
REPLACE_WITH = lambda ids: (6, False, ids)




    

##########################################################################################################






class fleet_map_sheet(models.Model):
    _name = 'fleet.map.sheet'
    _description = 'Fleet Map Sheet' 
    
    def _get_odometer(self, cr, uid, ids, field_name, arg, context):
        res = dict.fromkeys(ids, 0)
        for record in self.browse(cr,uid,ids,context=context):
            if field_name == 'odometer_start':
                if record.odometer_start_id.id:
                    res[record.id]  = record.odometer_start_id.value
                else:
                    ids = self.pool.get('fleet.vehicle.odometer').search(cr, uid, [('vehicle_id', '=', record.vehicle_id.id),('date','<=',record.date_start)], limit=1, order='date desc')
                    if len(ids) > 0:
                        res[record.id] = self.pool.get('fleet.vehicle.odometer').browse(cr, uid, ids[0], context=context).value   
                    else:                    # chiar sa nu fie nici unul?
                        if record.odometer_end_id.id:
                            res[record.id] = record.odometer_end_id.value  - record.distance_total              
            if field_name == 'odometer_end':
                if record.odometer_end_id.id:
                    res[record.id]  = record.odometer_end_id.value
                else:
                    ids = self.pool.get('fleet.vehicle.odometer').search(cr, uid, [('vehicle_id', '=', record.vehicle_id.id),('date','>=',record.date_end)], limit=1, order='date')
                    if len(ids) > 0:
                        res[record.id] = self.pool.get('fleet.vehicle.odometer').browse(cr, uid, ids[0], context=context).value                
                    else:
                        res[record.id] = record.odometer_start   + record.distance_total                         
        return res       
     

    def _set_odometer(self, cr, uid, id, field_name, value, args=None, context=None):
        if value:
            for record in self.browse(cr,uid,[id],context=context):
                if field_name == 'odometer_start':             
                    data = {'value': value, 'date': record.date_start, 'vehicle_id': record.vehicle_id.id}
                    if record.odometer_start_id.id:
                        self.pool.get('fleet.vehicle.odometer').write(cr, uid, [record.odometer_start_id.id], data, context=context)
                    else:
                        res_id = record.odometer_start_id = self.pool.get('fleet.vehicle.odometer').create(cr, uid, data, context=context)
                        self.write(cr, uid, [id], {'odometer_start_id':res_id},context=context)
                        
                if field_name == 'odometer_end':
                    data = {'value': value, 'date': record.date_end, 'vehicle_id': record.vehicle_id.id}
                    if record.odometer_end_id.id:
                        self.pool.get('fleet.vehicle.odometer').write(cr, uid, [record.odometer_end_id.id], data, context=context)
                    else:
                        res_id = record.odometer_end_id = self.pool.get('fleet.vehicle.odometer').create(cr, uid, data, context=context)
                        self.write(cr, uid, [id], {'odometer_end_id':res_id},context=context)               
        return        



    def _amount_all(self, cr, uid, ids, field_name, arg, context=None):
        res = {}        
        for map_sheet in self.browse(cr, uid, ids, context=context):
            res[map_sheet.id] = {
                'liter_total': 0.0,
                'amount_total': 0.0,
                'distance_total': 0.0,
                'norm_cons': 0.0,
                'odometer_end': 0.0,
            }
            liter = amount = 0.0
            distance_total = 0.0 
            norm_cons = 0.0             
            for log_fuel in map_sheet.log_fuel_ids:
                liter += log_fuel.liter
                amount +=  log_fuel.amount
            res[map_sheet.id]['liter_total'] = liter     
            res[map_sheet.id]['amount_total'] = amount
            
            for route in map_sheet.route_log_ids:
                distance_total += route.distance 
                norm_cons += route.norm_cons           
            res[map_sheet.id]['distance_total'] = distance_total
            res[map_sheet.id]['norm_cons'] =  norm_cons  #distance_total * map_sheet.vehicle_id.avg_cons / 100
            res[map_sheet.id]['odometer_end'] = map_sheet.odometer_start + distance_total
#            self._set_odometer(cr, uid, [map_sheet.id],'odometer_end',map_sheet.odometer_start + distance_total,context=context)

            
        return res

    
    def _get_map_sheet_fuel(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('fleet.vehicle.log.fuel').browse(cr, uid, ids, context=context):
            result[line.map_sheet_id.id] = True
        return result.keys()


    def _get_map_sheet_route(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('fleet.route.log').browse(cr, uid, ids, context=context):
            result[line.map_sheet_id.id] = True
        return result.keys()        
    
 
    def _get_reservoir_level_start(self, cr, uid, ids, prop, unknow_none, context=None):
        res = {}
        for record in self.browse(cr, uid, ids, context=context):           
            level_obj = self.pool.get('fleet.reservoir.level')
            res[record.id] = level_obj.get_level_to(cr, uid, record.vehicle_id.id, record.date_start)
        return res  

    def _get_reservoir_level_end(self, cr, uid, ids, prop, unknow_none, context=None):
        res = {}
        for record in self.browse(cr, uid, ids, context=context):           
            level_obj = self.pool.get('fleet.reservoir.level')
            res[record.id] = level_obj.get_level_to(cr, uid, record.vehicle_id.id, record.date_end)
        return res   
    
    _columns = {  
        'name':         fields.char('Number', size=20, required=True, readonly=True, states={'draft':[('readonly',False)]}),
        'date':         fields.date('Date', required=True, readonly=True, states={'draft':[('readonly',False)]}),
        'vehicle_id':   fields.many2one('fleet.vehicle', 'Vehicle', required=True, help='Vehicle',readonly=True, states={'draft':[('readonly',False)]}),
        'category_id':  fields.related('vehicle_id','category_id', type="many2one", readonly=True,  relation='fleet.vehicle.category', string="Vehicle Category"),
        'driver_id':    fields.many2one('res.partner', 'Driver', help='Driver of the vehicle',states={'done':[('readonly',True)]}),
        'driver2_id':   fields.many2one('res.partner', 'Backup Driver', help='Backup driver of the vehicle',states={'done':[('readonly',True)]}),
        'avg_cons':     fields.related('vehicle_id','avg_cons', type="float", readonly=True, string="Average Consumption"),

                
        'odometer_start_id':  fields.many2one('fleet.vehicle.odometer', string= 'ID Odometer start',  domain="[('vehicle_id','=',vehicle_id)]",   states={'done':[('readonly',True)]}),
        'odometer_end_id':    fields.many2one('fleet.vehicle.odometer', string= 'ID Odometer end',    domain="[('vehicle_id','=',vehicle_id)]",   states={'done':[('readonly',True)]}),

        'date_start':         fields.datetime('Date Start', help='Date time at the start of this map sheet',   states={'done':[('readonly',True)]}),
        'date_start_old':     fields.dummy('Date Start', type='datetime' ),
        'date_end':           fields.datetime('Date End',   help='Date time at the end of this map sheet',     states={'done':[('readonly',True)]}),
  
        'odometer_start': fields.function(_get_odometer, fnct_inv=_set_odometer, type='float', 
                                           string= _('Odometer Start'), help='Odometer measure of the vehicle at the start of this map sheet',
                                           states={'done':[('readonly',True)]}),
        'odometer_end':   fields.function(_get_odometer, fnct_inv=_set_odometer, type='float', 
                                          string= _('Odometer End'),   help='Odometer measure of the vehicle at the end of this map sheet',
                                           states={'done':[('readonly',True)]}),
      
        'state': fields.selection([('draft', 'Draft'), ('open','In Progress'), ('done', 'Done'), ('cancel', 'Cancelled')], string='Status',  readonly=True,      
            help="When the Map Sheet is created the status is set to 'Draft'.\n\
                  When the Map Sheet is in progress the status is set to 'In Progress' .\n\
                  When the Map Sheet is closed, the status is set to 'Done'."),
       



        'log_fuel_ids': fields.one2many('fleet.vehicle.log.fuel','map_sheet_id','Fuel log',states={'done':[('readonly',True)]}),
        'route_log_ids': fields.one2many('fleet.route.log','map_sheet_id','Route Logs',states={'done':[('readonly',True)]}),
                      
        'liter_total': fields.function(_amount_all, type='float', string='Total Liter',
            store={'fleet.vehicle.log.fuel': (_get_map_sheet_fuel, None, 10),
                   'fleet.route.log': (_get_map_sheet_route, None,  10), }, multi="sums", help="The total liters"),
                
        'amount_total': fields.function(_amount_all,  type='float', string='Total Amount',
            store={'fleet.vehicle.log.fuel': (_get_map_sheet_fuel, None, 10),
                   'fleet.route.log': (_get_map_sheet_route, None,  10), }, multi="sums", help="The total amount for fuel"),
       
        'distance_total':fields.function(_amount_all,  type='float', string='Total distance',
            store={'fleet.vehicle.log.fuel': (_get_map_sheet_fuel, None, 10),
                   'fleet.route.log': (_get_map_sheet_route, None,  10), }, multi="odmeter", help="The total distance"),
                
        'norm_cons':  fields.function(_amount_all, type='float',  string='Normal Consumption',
            store={'fleet.vehicle.log.fuel': (_get_map_sheet_fuel, None, 10),
                   'fleet.route.log': (_get_map_sheet_route, None, 10), }, multi="odmeter", help="The Normal Consumption"),
                
        'company_id': fields.many2one('res.company','Company',required=True,states={'done':[('readonly',True)]}), 
        
        'reservoir_level_start': fields.function(_get_reservoir_level_start, type="float", string='Level Reservoir Start', 
                                                 store=False, help="Fuel level in the reservoir at the beginning of road map"),
        'reservoir_level_end': fields.function(_get_reservoir_level_end, type="float", string='Level Reservoir End', 
                                                 store=False, help="Fuel level in the reservoir at the beginning of road map"),
                              
    }
    
    def _conv_local_datetime_to_utc(self,cr, uid, date, context):
        tz_name = context['tz']             
        local = pytz.timezone (tz_name)
        naive =  datetime.strptime (date, "%Y-%m-%d %H:%M:%S")
        local_dt = local.localize(naive, is_dst=None)
        utc_dt = local_dt.astimezone (pytz.utc)
        return utc_dt.strftime('%Y-%m-%d %H:%M:%S')
    
    
    def _get_default_date_start(self, cr, uid, context):
        if context and 'date' in context:
            res = self._conv_local_datetime_to_utc(cr, uid, context['date'][:10]+' 00:00:00', context)
        else:
            res = time.strftime('%Y-%m-%d %H:%M:%S')
        return res

    def _get_default_date_end(self, cr, uid, context):
        if context and 'date' in context:
            res = self._conv_local_datetime_to_utc(cr, uid, context['date'][:10]+' 23:59:59', context)
        else:
            res = time.strftime('%Y-%m-%d %H:%M:%S')
        return res

    
    
    
    _defaults = {
        'state': 'draft',
        'date': lambda self, cr, uid, context : context['date'] if context and 'date' in context else time.strftime('%Y-%m-%d'),
        'date_start': _get_default_date_start,
        'date_end': _get_default_date_end,
        'name': lambda x, y, z, c: x.pool.get('ir.sequence').next_by_code(y, z, 'fleet.map.sheet') or '/',
        'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, 'mrp.production', context=c),
        'vehicle_id' : lambda self, cr, uid, context : context['vehicle_id'] if context and 'vehicle_id' in context else None 
    }


    def copy(self, cr, uid, id, default=None, context=None):
        if not default:
            default = {}
            
        record = self.browse(cr, uid, id, context=context)

        date_start = datetime.strptime(record.date_start,tools.DEFAULT_SERVER_DATETIME_FORMAT) 
        date_start = date_start + timedelta(days=1)
        date_start = datetime.strftime(date_start,tools.DEFAULT_SERVER_DATETIME_FORMAT)

        date_end = datetime.strptime(record.date_start,tools.DEFAULT_SERVER_DATETIME_FORMAT) 
        date_end = date_end + timedelta(days=1)
        date_end = datetime.strftime(date_end,tools.DEFAULT_SERVER_DATETIME_FORMAT)
        
        date = datetime.strptime(record.date,tools.DEFAULT_SERVER_DATE_FORMAT) 
        date = date + timedelta(days=1)
        date = datetime.strftime(date,tools.DEFAULT_SERVER_DATE_FORMAT)    
        #TODO: de introdus pozitii si pentru rute cu data incrementata      
        default.update({
            'log_fuel_ids':[],
            'name': self.pool.get('ir.sequence').next_by_code(cr, uid, 'fleet.map.sheet'),
            'date': date,
            'date_start': date_start,
            'date_start': date_end,
        })
        new_id = super(fleet_map_sheet, self).copy(cr, uid, id, default, context=context)
        return new_id


    def on_change_vehicle(self, cr, uid, ids, vehicle_id, context=None):
        if not vehicle_id:
            return {}        
        vehicle = self.pool.get('fleet.vehicle').browse(cr, uid, vehicle_id, context=context)                                 
        return {
            'value': {
                'driver_id': vehicle.driver_id.id,
                'driver2_id': vehicle.driver2_id.id,
            }
                
        }



    def on_change_date_start(self, cr, uid, ids, date_start,date_end, date_start_old, route_log_ids, context=None):
        # se determina diferenta din dintre data veche si noua data !!                         
        if len(ids) != 1:
            return {}
        
        if not date_start_old:
            date_start_old   = self.read(cr, uid, ids, ['date_start'], context=context)[0]['date_start']
        
        # map_sheet = self.browse(cr, uid, ids, context=context)[0]
        new_date_start_int = str_to_datetime(date_start)  
        old_date_start_int = str_to_datetime(date_start_old)
        
        date_dif = new_date_start_int - old_date_start_int
        
        new_date_end_int = str_to_datetime(date_end) 
        date_end = datetime_to_str(new_date_end_int + date_dif)   
          

        route_log_list = self.resolve_2many_commands(cr, uid, 'route_log_ids', route_log_ids, ['id','date_begin','date_end'], context=context)
        
        
        if len(route_log_ids) > 0:
            for i in range(len(route_log_ids)): 
                routes = [x for x in route_log_list if x['id'] == route_log_ids[i][1]]
                if routes:
                    route = routes[0]     
                    date_begin_int = str_to_datetime(route['date_begin'])
                    date_end_int = str_to_datetime(route['date_end'])
                    route_log_ids[i][2] = {'date_begin':datetime_to_str(date_begin_int+date_dif),
                                           'date_end':datetime_to_str(date_end_int+date_dif)}
                    route_log_ids[i][0] = 1
       
        return {
            'value': {'date_end':      date_end,
                      'date_start_old': date_start, 
                      'route_log_ids': route_log_ids}
        }
        
        
    def on_change_route_log(self, cr, uid, ids, route_log_ids, date_start, date_end, context=None):
        return {}
        if not route_log_ids: 
            return {}
        
        new_date_start = date_start
        new_date_end = date_end
        
        for route_log in  route_log_ids:
            values = route_log[2]
            if values and 'date_end' in values and  values['date_end']>new_date_end:
                new_date_end = values['date_end']
                
            if values and 'date_begin' in values and  values['date_begin']<new_date_start:
                new_date_start = values['date_begin']
                
 
        return {
            'value': {
             #   'date_start':new_date_start,
                'date_end':new_date_end,
            }
        }
 
        
    def write(self, cr, uid, ids, vals, context=None):
        
        for map_sheet in self.browse(cr, uid, ids, context=context):
            for fuel_log in map_sheet.log_fuel_ids:
                self.pool.get('fleet.vehicle.log.fuel').write(cr,uid,fuel_log.id, {'vehicle_id':map_sheet.vehicle_id.id},context=context)
            
            for route_log in map_sheet.route_log_ids:
                self.pool.get('fleet.route.log').write(cr,uid,route_log.id, {'vehicle_id':map_sheet.vehicle_id.id},context=context)            
            if map_sheet.odometer_start_id:
                self.pool.get('fleet.vehicle.odometer').write(cr,uid, map_sheet.odometer_start_id.id, {'vehicle_id':map_sheet.vehicle_id.id},context=context)
            if map_sheet.odometer_end_id:
                self.pool.get('fleet.vehicle.odometer').write(cr,uid, map_sheet.odometer_end_id.id, {'vehicle_id':map_sheet.vehicle_id.id},context=context)
        res = super(fleet_map_sheet, self).write(cr, uid, ids, vals, context=context) 
        return  res

    def unlink(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        """Allows to delete map sheet in draft,cancel states"""
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.state not in ['draft', 'cancel']:
                raise osv.except_osv(_('Invalid Action!'), _('Cannot delete a map sheet which is in state \'%s\'.') %(rec.state,))
        return super(fleet_map_sheet, self).unlink(cr, uid, ids, context=context)


        
    def button_dummy(self, cr, uid, ids, context=None):
        return True

    def action_get_log_fuel(self, cr, uid, ids, context=None):
        for record in self.browse(cr, uid, ids, context=context):
            fuel_log_ids = self.pool.get('fleet.vehicle.log.fuel').search(cr, uid, [('vehicle_id', '=', record.vehicle_id.id),
                                                                                    ('date_time','>=',record.date_start),
                                                                                    ('date_time','<=',record.date_end),
                                                                                    ('map_sheet_id','=',None)   ])    
            if len(fuel_log_ids) > 0: 
                self.pool.get('fleet.vehicle.log.fuel').write(cr,uid, fuel_log_ids,{'map_sheet_id': record.id}, context) 
        return True

    def action_get_route_log(self, cr, uid, ids, context=None):
        for record in self.browse(cr, uid, ids, context=context):
            log_route_ids = self.pool.get('fleet.route.log').search(cr, uid, [ ('vehicle_id', '=', record.vehicle_id.id),
                                                                               ('date_begin','>=',record.date_start[:10]),
                                                                               ('date_end','<=',record.date_end),
                                                                               ('map_sheet_id','=',None) ])     
            if len(log_route_ids) > 0:
                self.pool.get('fleet.route.log').write(cr,uid, log_route_ids,{'map_sheet_id': record.id}, context) 
        return True

    
    def action_open(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'open'})
        return True
    
    def action_done(self, cr, uid, ids, context=None):
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.distance_total == 0:
                raise osv.except_osv(_('Invalid Action!'), _('Cannot set done a map sheet which distance equal with zero.') )

        self.write(cr, uid, ids, {'state': 'done'})
        for map_sheet in self.browse(cr, uid, ids, context=context):
            for fuel_log in map_sheet.log_fuel_ids:
                self.pool.get('fleet.vehicle.log.fuel').write(cr,uid,fuel_log.id, {'state': 'done'}, context=context)
        return True


 



    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: