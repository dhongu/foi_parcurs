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




    @api.multi
    @api.depends('vehicle_id','date_start','distance_total')
    def _compute_odometer_start(self):
        print "_compute_odometer_start"
        for record in self:
            if record.odometer_start_id:
                record.odometer_start  = record.odometer_start_id.value
            else:
                odometer = self.env['fleet.vehicle.odometer'].search([('vehicle_id', '=', record.vehicle_id.id),('date','<=',record.date_start)], limit=1, order='date desc')
                if odometer:
                    record.odometer_start = odometer.value 
                    if not record.odometer_end_id:
                        record.odometer_end = record.odometer_start   + record.distance_total       
                else:                
                    if record.odometer_end_id:
                        record.odometer_start = record.odometer_end_id.value  - record.distance_total 
                    else:
                        record.odometer_start = 0   

    @api.multi
    @api.depends('vehicle_id','date_end','distance_total')
    def _compute_odometer_end(self):  
        print "_compute_odometer_end"   
        for record in self:
            if record.odometer_end_id:
                record.odometer_end  = record.odometer_end_id.value
            else:
                odometer = self.env['fleet.vehicle.odometer'].search([('vehicle_id', '=', record.vehicle_id.id),('date','>=',record.date_end)], limit=1, order='date')
                if  odometer:
                    record.odometer_end = odometer.value                
                else:
                    if record.odometer_start_id:
                        record.odometer_end = record.odometer_start_id.value   + record.distance_total  
                    else:
                        record.odometer_end = record.odometer_start   + record.distance_total                      
                
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


    @api.model
    def _get_default_date_start(self):
        res = None
        context = self.env.context
        if context and 'date' in context:
            res = self._conv_local_datetime_to_utc(cr, uid, context['date'][:10]+' 00:00:00', context)
        else:
            res = fields.Datetime.now()
        return res


    @api.model
    def _get_default_date_end(self):
        res = None
        context = self.env.context
        if context and 'date' in context:
            res = self._conv_local_datetime_to_utc(cr, uid, context['date'][:10]+' 23:59:59', context)
        else:
            res = fields.Datetime.now()
        return res   
    
    @api.model 
    def _get_default_date(self):
        res = None
        context = self.env.context
        if context and 'date' in context:
            res = context['date']
        else:
            res = fields.Date.today()
        return res 

    name  =        fields.Char(string='Number', size=20, required=True, readonly=True, states={'draft':[('readonly',False)]},
                               default=lambda self: self.env['ir.sequence'].next_by_code('fleet.map.sheet') or '/'  )
    
    date =         fields.Date(string='Date', required=True, readonly=True, states={'draft':[('readonly',False)]}, default=_get_default_date )
    vehicle_id =   fields.Many2one('fleet.vehicle', string='Vehicle', required=True, help='Vehicle',readonly=True, states={'draft':[('readonly',False)]} )
    category_id =  fields.Many2one(related='vehicle_id.category_id',  readonly=True,  relation='fleet.vehicle.category', string="Vehicle Category")
    driver_id =    fields.Many2one('res.partner',  string='Driver', help='Driver of the vehicle',states={'done':[('readonly',True)]})
    driver2_id =   fields.Many2one('res.partner',  string='Backup Driver', help='Backup driver of the vehicle',states={'done':[('readonly',True)]})
    avg_cons =     fields.Float(related='vehicle_id.avg_cons',   readonly=True, string="Average Consumption")


    date_start =       fields.Datetime(string = 'Date Start', help='Date time at the start of this map sheet',   
                                       states={'done':[('readonly',True)]}, default=_get_default_date_start)
    date_start_old =   fields.Datetime(string = 'Date Start')
    date_end =         fields.Datetime(string = 'Date End',   help='Date time at the end of this map sheet',    
                                        states={'done':[('readonly',True)]}, default=_get_default_date_end)
  

    odometer_end  =  fields.Float(compute='_compute_odometer_end', inverse='_set_odometer_end' ,   states={'done':[('readonly',True)]} ,
                                          string=  'Odometer End' ,  
                                           help='Odometer measure of the vehicle at the end of this map sheet' )  
 
    odometer_start = fields.Float(compute='_compute_odometer_start', inverse='_set_odometer_start' ,  states={'done':[('readonly',True)]}  ,  
                                           string=  'Odometer Start' , 
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
       

    log_fuel_ids = fields.One2many('fleet.vehicle.log.fuel','map_sheet_id', string='Fuel log', states={'done':[('readonly',True)]}, copy=False)
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
                              
    
    @api.one
    @api.constrains('date_start', 'date_end')
    def _check_dates(self):
        if self.date_start > self.date_end:
            raise ValidationError( _("Map Sheet end-date (%s) must be greater then start-date (%s)") % (self.date_end, self.date_start ) )

    
    def _conv_local_datetime_to_utc(self,cr, uid, date, context):
        tz_name = context['tz']             
        local = pytz.timezone (tz_name)
        naive =  datetime.strptime (date, "%Y-%m-%d %H:%M:%S")
        local_dt = local.localize(naive, is_dst=None)
        utc_dt = local_dt.astimezone (pytz.utc)
        return utc_dt.strftime('%Y-%m-%d %H:%M:%S') 
  
    """
    _defaults = {

        'name': lambda x, y, z, c: x.pool.get('ir.sequence').next_by_code(y, z, 'fleet.map.sheet') or '/',        
        'vehicle_id' : lambda self, cr, uid, context : context['vehicle_id'] if context and 'vehicle_id' in context else None 
    }
    """
    
    @api.multi
    def copy(self,  default=None ):
        if not default:
            default = {}
            
        record = self

        date_start = fields.Datetime.from_string(record.date_start) + timedelta(days=1)
        date_start = fields.Datetime.to_string(date_start)
        
        #date_start = datetime.strptime(record.date_start,tools.DEFAULT_SERVER_DATETIME_FORMAT) 
        #date_start = date_start + timedelta(days=1)
        #date_start = datetime.strftime(date_start,tools.DEFAULT_SERVER_DATETIME_FORMAT)


        date_end = fields.Datetime.from_string(record.date_end) + timedelta(days=1)
        date_end = fields.Datetime.to_string(date_end)
        
        
        #date_end = datetime.strptime(record.date_start,tools.DEFAULT_SERVER_DATETIME_FORMAT) 
        #date_end = date_end + timedelta(days=1)
        #date_end = datetime.strftime(date_end,tools.DEFAULT_SERVER_DATETIME_FORMAT)


        date = fields.Date.from_string(record.date) + timedelta(days=1)
        date = fields.Date.to_string(date)
                
        #date = datetime.strptime(record.date,tools.DEFAULT_SERVER_DATE_FORMAT) 
        #date = date + timedelta(days=1)
        #date = datetime.strftime(date,tools.DEFAULT_SERVER_DATE_FORMAT)
        
            
        #TODO: de introdus pozitii si pentru rute cu data incrementata      
        default.update({
            'log_fuel_ids':[],
            'name': self.env['ir.sequence'].next_by_code( 'fleet.map.sheet'),
            'date': date,
            'date_start': date_start,
            'date_start': date_end,
        })
        new_id = super(fleet_map_sheet, self).copy( default )
        return new_id

    @api.multi
    def on_change_vehicle(self, vehicle_id):
        res = {}
        if not vehicle_id:
            return res        
        vehicle = self.env['fleet.vehicle'].browse(vehicle_id)                                 
        if vehicle:
            res = {
                'value': {
                    'driver_id': vehicle.driver_id.id,
                    'driver2_id': vehicle.driver2_id.id,
                    }
                }    
        return res



    @api.multi
    def on_change_date_start(self,  date_start, date_end, date_start_old, route_log_ids ):
        # se determina diferenta din dintre data veche si noua data !!                         
        if len(self.ids) != 1:
            return {}
        

        
        if not date_start_old:
            #date_start_old   = self.read(cr, uid, ids, ['date_start'], context=context)[0]['date_start']
            date_start_old = self.date_start
        
        # map_sheet = self.browse(cr, uid, ids, context=context)[0]
        new_date_start_int = fields.Datetime.from_string(date_start)  
        old_date_start_int = fields.Datetime.from_string(date_start_old)
        
        date_dif = new_date_start_int - old_date_start_int
        
        new_date_end_int = fields.Datetime.from_string(date_end) 
        date_end = fields.Datetime.to_string(new_date_end_int + date_dif)   
          

        route_log_list = self.resolve_2many_commands( 'route_log_ids', route_log_ids, ['id','date_begin','date_end'])
        
        
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
            'value': {'date_end':       date_end,
                      'date_start_old': date_start, 
                      'route_log_ids':  route_log_ids}
        }
        
    @api.multi    
    def on_change_route_log(self,   route_log_ids, date_start, date_end ):
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
 
    @api.multi
    def write(self, vals):
        
        for map_sheet in self:
            map_sheet.log_fuel_ids.write({'vehicle_id':map_sheet.vehicle_id.id})
            map_sheet.route_log_ids.write({'vehicle_id':map_sheet.vehicle_id.id})
            if map_sheet.odometer_start_id:
                map_sheet.odometer_start_id.write({'vehicle_id':map_sheet.vehicle_id.id})
            if map_sheet.odometer_end_id:
                map_sheet.odometer_end_id.write({'vehicle_id':map_sheet.vehicle_id.id})
            

        res = super(fleet_map_sheet, self).write( vals ) 
        return  res
    
    
    @api.multi
    def unlink(self):
        """Allows to delete map sheet in draft,cancel states"""
        for rec in self:
            if rec.state not in ['draft', 'cancel']:
                raise Warning(  _('Cannot delete a map sheet which is in state \'%s\'.') %(rec.state,))
        return super(fleet_map_sheet, self).unlink()


    @api.multi    
    def button_dummy(self):
        return True

    @api.multi
    def action_get_log_fuel(self):
        for record in self:
            fuel_log_ids = self.env['fleet.vehicle.log.fuel'].search(  [('vehicle_id', '=', record.vehicle_id.id),
                                                                            ('date_time','>=',record.date_start),
                                                                            ('date_time','<=',record.date_end),
                                                                            ('map_sheet_id','=',None)   ])    
            if fuel_log_ids: 
                fuel_log_ids.write({'map_sheet_id': record.id})
        return True

    @api.multi
    def action_get_route_log(self):
        for record in self:
            log_route_ids = self.env['fleet.route.log'].search( [ ('vehicle_id', '=', record.vehicle_id.id),
                                                                       ('date_begin','>=',record.date_start[:10]),
                                                                       ('date_end','<=',record.date_end),
                                                                       ('map_sheet_id','=',None) ])     
            if log_route_ids:
                fuel_log_ids.write({'map_sheet_id': record.id})
        return True

    @api.multi
    def action_open(self):
        self.write( {'state': 'open'})
        return True

    @api.multi
    def action_done(self):
        for rec in self:
            if rec.distance_total == 0:
                raise Warning( _('Cannot set done a map sheet which distance equal with zero.') )

        self.write( {'state': 'done'})
        for map_sheet in self:
            map_sheet.log_fuel_ids.write({'state': 'done'})
        return True


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: