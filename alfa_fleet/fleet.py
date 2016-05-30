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

from datetime import datetime, timedelta, date
import math





class fleet_map_sheet(models.Model):
    _name = 'fleet.map.sheet'
    _description = 'Fleet Map Sheet' 



    @api.one
    @api.depends('route_log_ids','odometer_start', 'odometer_end', 'odometer_start_id','odometer_end_id')
    def _compute_odometer(self):
        if self.odometer_start_id:
            self.odometer_start  = self.odometer_start_id.value
        else:
            odometer = self.env['fleet.vehicle.odometer'].search([('vehicle_id', '=', self.vehicle_id.id),('date','<=',self.date_start)], limit=1, order='date desc')
            if odometer:
                self.odometer_start = odometer.value 
                if not self.odometer_end_id:
                    self.odometer_end = self.odometer_start   + self.distance_total       
            else:                
                if self.odometer_end_id:
                    self.odometer_start = self.odometer_end_id.value  - self.distance_total 
                else:
                    self.odometer_start = 0   

        if self.odometer_end_id:
            self.odometer_end  = self.odometer_end_id.value
        else:
            odometer = self.env['fleet.vehicle.odometer'].search([('vehicle_id', '=', self.vehicle_id.id),('date','>=',self.date_end)], limit=1, order='date')
            if  odometer:
                self.odometer_end = odometer.value                
            else:
                self.odometer_end = self.odometer_start   + self.distance_total  



    @api.one
    def _get_odometer_start(self):
        if self.odometer_start_id:
            self.odometer_start  = self.odometer_start_id.value
        else:
            odometer = self.env['fleet.vehicle.odometer'].search([('vehicle_id', '=', self.vehicle_id.id),('date','<=',self.date_start)], limit=1, order='date desc')
            if odometer:
                self.odometer_start = odometer.value 
                if not self.odometer_end_id:
                    self.odometer_end = self.odometer_start   + self.distance_total       
            else:                
                if self.odometer_end_id:
                    self.odometer_start = self.odometer_end_id.value  - self.distance_total 
                else:
                    self.odometer_start = 0   

    @api.one
    def _get_odometer_end(self):        
        if self.odometer_end_id:
            self.odometer_end  = self.odometer_end_id.value
        else:
            odometer = self.env['fleet.vehicle.odometer'].search([('vehicle_id', '=', self.vehicle_id.id),('date','>=',self.date_end)], limit=1, order='date')
            if  odometer:
                self.odometer_end = odometer.value                
            else:
                if self.odometer_start_id:
                    self.odometer_end = self.odometer_start_id.value   + self.distance_total  
                else:
                    self.odometer_end = self.odometer_start   + self.distance_total                      
                
    @api.one
    def _set_odometer_start(self):
        data = {'value': self.odometer_start, 'date': self.date_start, 'vehicle_id': self.vehicle_id.id}
        if self.odometer_start_id:
            self.odometer_start_id.write(data)
        else:
            self.odometer_start_id = self.env['fleet.vehicle.odometer'].create( data)

    @api.one
    def _set_odometer_end(self):
        data = {'value': self.odometer_end, 'date': self.date_end, 'vehicle_id': self.vehicle_id.id}
        if self.odometer_end_id:
            self.odometer_end_id.write(data)
        else:
            self.odometer_end_id = self.env['fleet.vehicle.odometer'].create( data)            

        
            
            
    @api.one
    @api.depends('route_log_ids','log_fuel_ids')
    def _compute_amount_all(self):
        liter = amount = 0.0
        distance_total = 0.0 
        norm_cons = 0.0             
        for log_fuel in self.log_fuel_ids:
            liter += log_fuel.liter
            amount +=  log_fuel.amount
        self.liter_total = liter     
        self.amount_total = amount
        
        for route in self.route_log_ids:
            distance_total += route.distance 
            norm_cons += route.norm_cons           
        self.distance_total  = distance_total
        self.norm_cons  =  norm_cons  #distance_total * map_sheet.vehicle_id.avg_cons / 100
        #self.odometer_end  = map_sheet.odometer_start + distance_total
#            self._set_odometer(cr, uid, [map_sheet.id],'odometer_end',map_sheet.odometer_start + distance_total,context=context)

            
        
     

    @api.one
    @api.depends('vehicle_id','date_start')
    def _compute_reservoir_level_start(self):
        if self.vehicle_id:
            self.reservoir_level_start =   self.env['fleet.reservoir.level'].get_level_to( self.vehicle_id.id, self.date_start)     
 

    @api.one
    @api.depends('vehicle_id','date_end')
    def _compute_reservoir_level_end(self):
        if self.vehicle_id:
            self.reservoir_level_end =  self.env['fleet.reservoir.level'].get_level_to( self.vehicle_id.id, self.date_end)  



    name  =        fields.Char(string='Number', size=20, required=True, readonly=True, states={'draft':[('readonly',False)]})
    date =         fields.Date(string='Date', required=True, readonly=True, states={'draft':[('readonly',False)]})
    vehicle_id =   fields.Many2one('fleet.vehicle', string='Vehicle', required=True, help='Vehicle',readonly=True, states={'draft':[('readonly',False)]})
    category_id =  fields.Many2one(related='vehicle_id.category_id',  readonly=True,  relation='fleet.vehicle.category', string="Vehicle Category")
    driver_id =    fields.Many2one('res.partner',  string='Driver', help='Driver of the vehicle',states={'done':[('readonly',True)]})
    driver2_id =   fields.Many2one('res.partner',  string='Backup Driver', help='Backup driver of the vehicle',states={'done':[('readonly',True)]})
    avg_cons =     fields.Float(related='vehicle_id.avg_cons',   readonly=True, string="Average Consumption")

                


    date_start =       fields.Datetime(string = 'Date Start', help='Date time at the start of this map sheet',   states={'done':[('readonly',True)]})
    date_start_old =   fields.Datetime(string = 'Date Start')
    date_end =         fields.Datetime(string = 'Date End',   help='Date time at the end of this map sheet',     states={'done':[('readonly',True)]})
  

    odometer_end =  fields.Float(_compute='_compute_odometer', inverse='_set_odometer_end' ,   states={'done':[('readonly',True)]} ,
                                          string=  'Odometer End' ,  store=False,
                                           help='Odometer measure of the vehicle at the end of this map sheet' )  
 
    odometer_start = fields.Float(compute='_compute_odometer', inverse='_set_odometer_start' ,  states={'done':[('readonly',True)]}  ,  
                                           string=  'Odometer Start' , store=False,
                                           help='Odometer measure of the vehicle at the start of this map sheet' )
    

    

    
    odometer_start_id =  fields.Many2one('fleet.vehicle.odometer', string = 'ID Odometer start', 
                                          domain="[('vehicle_id','=',vehicle_id)]",   states={'done':[('readonly',True)]})
  
    
    odometer_end_id =    fields.Many2one('fleet.vehicle.odometer', string = 'ID Odometer end',   
                                          domain="[('vehicle_id','=',vehicle_id)]",   states={'done':[('readonly',True)]})
      
    state = fields.Selection([('draft', 'Draft'), ('open','In Progress'), ('done', 'Done'), ('cancel', 'Cancelled')], 
                                string='Status',  readonly=True,   default='draft',     
                                help="When the Map Sheet is created the status is set to 'Draft'.\n\
                                      When the Map Sheet is in progress the status is set to 'In Progress' .\n\
                                      When the Map Sheet is closed, the status is set to 'Done'.")
       

    log_fuel_ids = fields.One2many('fleet.vehicle.log.fuel','map_sheet_id', string='Fuel log', states={'done':[('readonly',True)]})
    route_log_ids = fields.One2many('fleet.route.log','map_sheet_id', string='Route Logs', states={'done':[('readonly',True)]})
                      
    liter_total = fields.Float(compute='_compute_amount_all',   string='Total Liter', store=True, help="The total liters")
                
    amount_total = fields.Float(compute='_compute_amount_all',    string='Total Amount', store=True, help="The total amount for fuel")
       
    distance_total = fields.Float(compute='_compute_amount_all',    string='Total distance',  store=True, help="The total distance")
            
    norm_cons = fields.Float(compute='_compute_amount_all',    string='Normal Consumption', store=True, help="The Normal Consumption")
                
    company_id = fields.Many2one('res.company','Company',required=True,states={'done':[('readonly',True)]},
                                 default=lambda self: self.env['res.company']._company_default_get('fleet.map.sheet'))
  
     
    reservoir_level_start = fields.Float(compute='_compute_reservoir_level_start',  string='Level Reservoir Start', 
                                                 store=False, help="Fuel level in the reservoir at the beginning of road map")
    reservoir_level_end = fields.Float(compute='_compute_reservoir_level_end', string='Level Reservoir End', 
                                                 store=False, help="Fuel level in the reservoir at the beginning of road map")
                              
    
    
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
            res = fields.Datetime.now()
        return res



    def _get_default_date_end(self, cr, uid, context):
        if context and 'date' in context:
            res = self._conv_local_datetime_to_utc(cr, uid, context['date'][:10]+' 23:59:59', context)
        else:
            res = fields.Datetime.now()
        return res   
     
    def _get_default_date(self, cr, uid, context):
        if context and 'date' in context:
            res = context['date']
        else:
            res = fields.Date.today()()
        return res   
    
    _defaults = {
        'date': _get_default_date,
        'date_start': _get_default_date_start,
        'date_end': _get_default_date_end,
        'name': lambda x, y, z, c: x.pool.get('ir.sequence').next_by_code(y, z, 'fleet.map.sheet') or '/',
        
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
        new_date_start_int = fields.Datetime.from_string(date_start)  
        old_date_start_int = fields.Datetime.from_string(date_start_old)
        
        date_dif = new_date_start_int - old_date_start_int
        
        new_date_end_int = fields.Datetime.from_string(date_end) 
        date_end = fields.Datetime.to_string(new_date_end_int + date_dif)   
          

        route_log_list = self.resolve_2many_commands(cr, uid, 'route_log_ids', route_log_ids, ['id','date_begin','date_end'], context=context)
        
        
        if len(route_log_ids) > 0:
            for i in range(len(route_log_ids)): 
                routes = [x for x in route_log_list if x['id'] == route_log_ids[i][1]]
                if routes:
                    route = routes[0]     
                    date_begin_int = fields.Datetime.from_string(route['date_begin'])
                    date_end_int = fields.Datetime.from_string(route['date_end'])
                    route_log_ids[i][2] = {'date_begin':fields.Datetime.to_string(date_begin_int+date_dif),
                                           'date_end':fields.Datetime.to_string(date_end_int+date_dif)}
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
                raise Warning(  _('Cannot delete a map sheet which is in state \'%s\'.') %(rec.state,))
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
                raise Warning( _('Cannot set done a map sheet which distance equal with zero.') )

        self.write(cr, uid, ids, {'state': 'done'})
        for map_sheet in self.browse(cr, uid, ids, context=context):
            for fuel_log in map_sheet.log_fuel_ids:
                self.pool.get('fleet.vehicle.log.fuel').write(cr,uid,fuel_log.id, {'state': 'done'}, context=context)
        return True


 


 
class fleet_route_log(models.Model):
    _name = 'fleet.route.log'
    _description = 'Route Log'

 
    @api.model
    def _get_default_date_begin(self):
        res = None
        context = self.env.context
        if  'date' in context:
            res = context['date']
            date_end = res
            if context and 'route_log_ids' in context:
                route_log_ids = context['route_log_ids']
                for route_log in  route_log_ids:
                    if route_log[0] == 4:
                         route_log_obj = self.browse(route_log[1])
                         date_end = route_log_obj.date_end       
                    elif route_log[0] == 0 or route_log[0] == 1:
                        values = route_log[2]
                        if values and 'date_end' in values:
                            date_end = values['date_end']
                    if date_end > res :             
                        res =  date_end
        return res

    """
    @api.model
    def _get_default_vehicle_id(self):
        context =  self.env.context or {}
        res = context['vehicle_id'] if context and 'vehicle_id' in context else None  
        return  res
    """

 
    name       = fields.Char(compute='_compute_route_name', string="Name", store=False)
    scope_id   =  fields.Many2one('fleet.scope', string='Scope', states={'done':[('readonly',True)]})
    date_begin = fields.Datetime(string='Date Begin', states={'done':[('readonly',True)]}, default=_get_default_date_begin)
    date_end   =   fields.Datetime(string='Date End', states={'done':[('readonly',True)]}, default=_get_default_date_begin)
    week_day   =   fields.Integer(compute='_compute_week_day',  string='Name', store=False)
    route_id   =   fields.Many2one('fleet.route', string='Route', states={'done':[('readonly',True)]})
    vehicle_id = fields.Many2one('fleet.vehicle', string='Vehicle', states={'done':[('readonly',True)]},  ) #default=_get_default_vehicle_id )   
    map_sheet_id =   fields.Many2one('fleet.map.sheet', string='Map Sheet', 
                                     domain="['&',('vehicle_id','=',vehicle_id),('date_start','<=',date_begin),('date_end','>=',date_end)]")
    distance  =      fields.Float(string='Distance', states={'done':[('readonly',True)]})   
    norm_cons =  fields.Float(compute='_compute_norm_cons',    string='Normal Consumption',   
                              store=True,  help="The Normal Consumption", states={'done':[('readonly',True)]})
    state     =    fields.Selection([('draft', 'Draft'),  ('done', 'Done')], string='Status',   default='draft',    
                                help="When the Route Log is created the status is set to 'Draft'.\n\
                                      When the Route Log is closed, the status is set to 'Done'.")


    
    _order = "date_begin"

    @api.one
    @api.depends('distance','vehicle_id.avg_cons')
    def _compute_norm_cons(self):
        if self.vehicle_id:
            self.norm_cons =  self.distance * self.vehicle_id.avg_cons / 100


    @api.one
    @api.depends('route_id.name')
    def _compute_route_name(self):
        if self.route_id:
            self.name =  self.route_id.name  
    

    @api.one
    @api.depends('date_begin')
    def _compute_week_day(self):
        date_int =   fields.Datetime.from_string(self.date_begin)
        self.week_day = date_int.strftime('%w')


     
    @api.one
    @api.constrains('date_begin', 'date_end')
    def _check_dates(self):
        if self.date_begin > self.date_end:
            raise ValidationError("Route end-date must be greater then route begin-date")
     
     
    """ 
    def _check_dates(self, cr, uid, ids, context=None):
        if context == None:
            context = {}
        route_log = self.browse(cr, uid, ids[0], context=context)
        start = route_log.date_begin or False
        end = route_log.date_end or False
        if start and end :
            if start > end:
                return False
##            else:
##                res = self.search(cr, uid, [('vehicle_id','=',route_log.vehicle_id.id),('date_begin')])
##    start < date_begin < end or date_begin < start < date_end
        return True

    _constraints = [
        (_check_dates, 'Error ! Route end-date must be greater then route start-begin', ['date_begin','date_end'])
    ]
    """
    
    @api.multi
    def on_change_route(self, route_id, distance, date_begin,):
        
        context = self.env.context
        domain = []
        if context and 'route_log_ids' in context:
            route_log_ids = context['route_log_ids']
            prev_route_id = None
            for route_log in  route_log_ids:            
                if route_log[0] == 4:
                     route_log_obj = self.browse(route_log[1])
                     date_end = route_log_obj.date_end
                     route_id = route_log_obj.route_id.id       
                elif route_log[0] == 0 or route_log[0] == 1:
                    values = route_log[2]
                    if values and 'date_end' in values and route_id in values :
                        date_end = values['date_end']
                        route_id = values['route_id']
                if date_end <= self.date_begin :             
                    prev_route_id = route_id  
            if prev_route_id:
                 prev_route = self.env['fleet.route'].browse(prev_route_id)
                 domain = domain.append(('from_loc_id','=',prev_route.to_loc_id.id)) 
        
        value = {}
        if route_id and date_begin:
            route = self.env['fleet.route'].browse( route_id )   
            date_int = fields.Datetime.from_string(date_begin)
            week_day = int(date_int.strftime('%w'))
            date_end = date_int  # datetime.strptime(date_begin,tools.DEFAULT_SERVER_DATETIME_FORMAT) 
            date_end = date_end + timedelta(hours=int(math.floor(route.duration)), minutes=int((route.duration%1) * 60) )
            date_end = fields.Datetime.to_string(date_end)    # datetime.strftime(date_end,tools.DEFAULT_SERVER_DATETIME_FORMAT)
            value = {
                'distance': route.distance,
                'date_end': date_end,
                'week_day': week_day
            }
       
        return {
            'value': value,
            'domain':{'route_id':domain}
        }

    def unlink(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        """Allows to delete route log in draft states"""
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.state not in ['draft', False]:
                raise Warning( _('Cannot delete a route log which is in state \'%s\'.') %(rec.state,))
        return super(fleet_route_log, self).unlink(cr, uid, ids, context=context)
    
    
    



class fleet_vehicle(models.Model):
    _inherit = 'fleet.vehicle'


    name = fields.Char(compute='_compute_vehicle_name', string="Name", store=True)
    indicative =     fields.Char(string='Indicative', size=32)
    driver2_id =     fields.Many2one('res.partner', string='Backup Driver', help='Backup driver of the vehicle')
    mass_cap =        fields.Float(string='Mass capacity')
    tachometer =      fields.Boolean(string='Tachometer', help="Status of tachometer")
    reservoir =       fields.Float(string='Reservoir capacity')
    reservoir_level = fields.Float(compute='_compute_reservoir_level' , string='Level Reservoir', store=False)
    loading_level =  fields.Float(string='Level of loading')
    mass_cap =       fields.Float(string='Mass capacity')  
    card_ids =      fields.Many2many('fleet.card', 'fleet_card_vehicle_rel', 'vehicle_id','card_id',  string='Cards')
    avg_cons =       fields.Float(string='Average Consumption',default=8.0)
    avg_speed =      fields.Float(string='Average Speed',default=70.0) 
    category_id =    fields.Many2one('fleet.vehicle.category', string='Vehicle Category')



    _sql_constraints = [  ('indicative_uniq', 'unique (indicative)', 'The Indicative must be unique !') ]

 
    
    @api.multi
    def act_show_map_sheet(self):
        """ This opens map sheet view to view and add new map sheet for this vehicle
            @return: the map sheet view
        """
        self.ensure_one()
        result = self.env.ref(self._module+'.fleet_map_sheet_act').read()[0]
        result['context'] = dict(self.env.context, default_vehicle_id=self.id ) 
        result['domain'] = [('vehicle_id', '=', self.id)]
        return result            
                           
                               
    @api.one
    @api.depends('license_plate')
    def _compute_vehicle_name(self):
        #self.name =self.indicative + ':' + self.model_id.brand_id.name + '/' + self.model_id.modelname + ' / ' + self.license_plate  
        self.name =  self.license_plate
   
    @api.one
    def _compute_reservoir_level(self):
        if not isinstance(self.id, models.NewId):
            self.reservoir_level = self.env['fleet.reservoir.level'].get_level(self.id)
    


class fleet_vehicle_log_fuel(models.Model):
    _inherit = 'fleet.vehicle.log.fuel'
    
 

    map_sheet_id =  fields.Many2one('fleet.map.sheet', string='Map Sheet', domain="['&',('vehicle_id','=',vehicle_id),('date_start','<=',date_time),('date_end','>=',date_time)]")
    fuel_id =  fields.Many2one('fleet.fuel', string='Fuel')
    card_id =  fields.Many2one('fleet.card', string='Card')
    full  =   fields.Boolean(string='To full', help="Fuel supply was made up to full")
    reservoir_level = fields.Float(compute='_compute_reservoir_level' , string='Level Reservoir', store=False)
    state = fields.Selection([('draft', 'Draft'),  ('done', 'Done')], string='Status',  readonly=True,     
                                help="When the Log Fuel is created the status is set to 'Draft'.\n\
                                      When the Log Fuel is closed, the status is set to 'Done'.")
    
    @api.one
    def _compute_reservoir_level(self):
        if self.vehicle_id and self.date_time:
            self.reservoir_level = self.env['fleet.reservoir.level'].get_level_to(self.vehicle_id.id, self.date_time)
    
    def on_change_vehicle(self, cr, uid, ids, vehicle_id, context=None):  
        if not vehicle_id:
            return {}       
        res = super(fleet_vehicle_log_fuel, self).on_change_vehicle(cr, uid, ids, vehicle_id, context=context) 
        res['value']['map_sheet_id'] = None
        return res




class fleet_vehicle_cost(models.Model):
    _inherit = 'fleet.vehicle.cost'

  

    date_time = fields.Datetime(string='Date Time', help='Date and time when the cost has been executed')
    # modific campul din data in datatimp ?
    #date = fields.Date(string='Date', help='Date and time when the cost has been executed',compute='_compute_get_date', inverse='_compute_set_date', store=True)
    year = fields.Char(string='Year', store=True, compute='_compute_year' )
    
    
    @api.one
    @api.depends('date')
    def _compute_year(self):   
        if self.date:
            self.year =  str(fields.Date.from_string(self.date).year)
    
    @api.multi
    def write(self, vals):
        if 'date_time' in vals and 'date' not in vals:
            vals['date'] = vals['date_time']
        if 'date' in vals and 'date_time' not in vals:
            vals['date_time'] = vals['date']
        res = super(fleet_vehicle_cost,self).write(vals)
        return res



class fleet_vehicle_odometer(models.Model):
    _inherit = 'fleet.vehicle.odometer'  
    
    date_time = fields.Datetime(string='Date Time')
    real = fields.Boolean(string='Is real', default=fields.Datetime.now )
    
        
    @api.multi
    def write(self, vals ):
        if 'date_time' in vals and 'date' not in vals:
            vals['date'] = vals['date_time']
        if 'date' in vals and 'date_time' not in vals:
            vals['date_time'] = vals['date']
        res = super(fleet_vehicle_odometer,self).write(  vals )
        return res 
       



class fleet_route(models.Model):
    _name = 'fleet.route'
    _description = 'Route'  


    name        = fields.Char(string='Name', store=False, compute='_compute_name')
    from_loc_id = fields.Many2one('fleet.location', string='From', help='From location', required=True)
    to_loc_id   = fields.Many2one('fleet.location', string='To',   help='To location',   required=True) 
    distance    = fields.Float('Distance')
    duration    = fields.Float('Duration')
    reverse     = fields.Many2one('fleet.route', string='Reverse route')  

    
    @api.one
    @api.depends('from_loc_id.name','to_loc_id.name')
    def _compute_name(self):    
        self.name = self.from_loc_id.name + '-' + self.to_loc_id.name     

    @api.multi
    def button_create_reverse(self):
        for route in self:
            if not route.reverse:
                new_route = route.copy({'from_loc_id':route.to_loc_id.id, 
                                        'to_loc_id':route.from_loc_id.id,
                                        'reverse':route.id})
                route.reverse = new_route


class fleet_card(models.Model):
    _name = 'fleet.card'
    _description = 'Fuel Card'
    
    name = fields.Char(string='Series card',  size=20, required=True)
    type_card = fields.Selection([('2', 'Own pomp'),('3','Rompetrol'),('4','Petrom'),('5','Lukoil'),('6','OMV')], string = 'Type Card' ) 
    vehicle_ids = fields.Many2many('fleet.vehicle', 'fleet_card_vehicle_rel', 'card_id', 'vehicle_id', string='Vehicles')
    log_fuel_ids = fields.One2many('fleet.vehicle.log.fuel','card_id',string='Fuel log')
    active =  fields.Boolean(string='Active',default=1)
    


    _sql_constraints = [  ('serie_uniq', 'unique (name)', 'The series must be unique !') ]
    
 


class fleet_fuel(models.Model):
    _name = 'fleet.fuel'
    _description = 'Fuel'
    
    name = fields.Char(string='Fuel',  size=75, required=True) 
    fuel_type = fields.Selection([('gasoline', 'Gasoline'), ('diesel', 'Diesel')], string = 'Fuel Type' )    
    
 

class fleet_scope(models.Model):
    _name = 'fleet.scope'
    _description = 'Scope'
    
    name = fields.Char(string='Scope',  size=75, required=True) 
    
 
 

class fleet_location(models.Model):
    'Pozitia unei locatii si afisare pozitie pe Google Maps'
    _name = 'fleet.location'
    _description = 'Location'
    
    
    name = fields.Char(string='Location',  size=100, required=True) 
    type = fields.Selection([ ('0','Other'),  ('1','Partner'),   ('2','Station')], string = 'Type'   )



"""
class fleet_location_type(osv.osv):
    _name = 'fleet.location.type'
    _description = 'Location type'
    
    name = fields.Char(string='Type',  size=100, required=True) 
   
 
"""
  


class fleet_vehicle_category(models.Model):
    _name = 'fleet.vehicle.category'
    _description = 'Vehicle Category'
    
    name = fields.Char(string='Category',  size=100, required=True) 
    code = fields.Char(string='Cod',  size=4, required=True) 



class fleet_reservoir_level(models.Model):  
    _name = 'fleet.reservoir.level'
    _description = 'Fleet Reservoir Level'
    
    date = fields.Date(string='Date', required=True)
    vehicle_id = fields.Many2one('fleet.vehicle', string='Vehicle', required=True)
    liter =   fields.Float('Liter')
     
 
    
    def get_level(self,cr, uid, vehicle_id, context=None):
        level = 0.0
        cr.execute("""SELECT  sum(liter) AS liter
              FROM fleet_vehicle_log_fuel join fleet_vehicle_cost on fleet_vehicle_log_fuel.cost_id = fleet_vehicle_cost.id
              WHERE vehicle_id = %s
           """,
           (vehicle_id,))
        results = cr.dictfetchone()
        if results:
            level = results['liter']
            if level is None:
                level = 0
        cr.execute("""SELECT  sum(norm_cons) AS liter
              FROM fleet_route_log
              WHERE vehicle_id = %s
           """,
           (vehicle_id,))        
        results = cr.dictfetchone() 
        if results and results['liter'] :
            level = level - results['liter']        
        
        return level      

    def get_level_to(self,cr, uid, vehicle_id, ToDate, context=None):
        level = 0.0
        cr.execute("""SELECT  sum(liter) AS liter
              FROM fleet_vehicle_log_fuel join fleet_vehicle_cost on fleet_vehicle_log_fuel.cost_id = fleet_vehicle_cost.id
              WHERE vehicle_id = %s and
                   date_time <= %s
           """,
           (vehicle_id,  ToDate,))
        results = cr.dictfetchone()
        if results and results['liter']:
            level = results['liter']
            if level is None:
                level = 0
        cr.execute("""SELECT  sum(norm_cons) AS liter
              FROM fleet_route_log
              WHERE vehicle_id = %s  and
                   date_end <= %s
           """,
           (vehicle_id, ToDate,))        
        results = cr.dictfetchone() 
        if results and results['liter']:
            level = level - results['liter']        
        
        return level   
      

           

 


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: