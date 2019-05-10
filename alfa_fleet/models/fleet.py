# -*- coding: utf-8 -*-
# ©  2015-2019 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details




from odoo import models, fields, api
from odoo.exceptions import UserError, RedirectWarning, ValidationError




class fleet_vehicle_log_fuel(models.Model):
    _inherit = 'fleet.vehicle.log.fuel'

    map_sheet_id = fields.Many2one('fleet.map.sheet', string='Map Sheet',
                                   domain="['&',('vehicle_id','=',vehicle_id),('date_start','<=',date_time),('date_end','>=',date_time)]")
    fuel_id = fields.Many2one('fleet.fuel', string='Fuel')
    card_id = fields.Many2one('fleet.card', string='Card')
    full = fields.Boolean(string='To full', help="Fuel supply was made up to full")
    reservoir_level = fields.Float(compute='_compute_reservoir_level', string='Level Reservoir', store=False)
    state = fields.Selection([('draft', 'Draft'), ('done', 'Done')], string='Status', readonly=True,
                             help="When the Log Fuel is created the status is set to 'Draft'.\n\
                                      When the Log Fuel is closed, the status is set to 'Done'.")

    @api.one
    def _compute_reservoir_level(self):
        if self.vehicle_id and self.date_time:
            self.reservoir_level = self.env['fleet.reservoir.level'].get_level_to(self.vehicle_id.id, self.date_time)

    @api.onchange('vehicle_id')
    def _onchange_vehicle(self):
        res = super(fleet_vehicle_log_fuel, self)._onchange_vehicle()
        self.map_sheet_id =  False
        return res



class fleet_vehicle_cost(models.Model):
    _inherit = 'fleet.vehicle.cost'

    date_time = fields.Datetime(string='Date Time', help='Date and time when the cost has been executed')
    # modific campul din data in datatimp ?
    # date = fields.Date(string='Date', help='Date and time when the cost has been executed',compute='_compute_get_date', inverse='_compute_set_date', store=True)
    year = fields.Char(string='Year', store=True, compute='_compute_year')

    @api.one
    @api.depends('date')
    def _compute_year(self):
        if self.date:
            self.year = str(fields.Date.from_string(self.date).year)

    @api.multi
    def write(self, vals):
        if 'date_time' in vals and 'date' not in vals:
            vals['date'] = vals['date_time']
        if 'date' in vals and 'date_time' not in vals:
            vals['date_time'] = vals['date']
        res = super(fleet_vehicle_cost, self).write(vals)
        return res


class fleet_vehicle_odometer(models.Model):
    _inherit = 'fleet.vehicle.odometer'

    date_time = fields.Datetime(string='Date Time')
    real = fields.Boolean(string='Is real', default=fields.Datetime.now)

    @api.multi
    def write(self, vals):
        if 'date_time' in vals and 'date' not in vals:
            vals['date'] = vals['date_time']
        if 'date' in vals and 'date_time' not in vals:
            vals['date_time'] = vals['date']
        res = super(fleet_vehicle_odometer, self).write(vals)
        return res


class fleet_route(models.Model):
    _name = 'fleet.route'
    _description = 'Route'

    name = fields.Char(string='Name', store=False, compute='_compute_name')
    from_loc_id = fields.Many2one('fleet.location', string='From', help='From location', required=True)
    to_loc_id = fields.Many2one('fleet.location', string='To', help='To location', required=True)
    distance = fields.Float('Distance')
    duration = fields.Float('Duration')
    dist_c1 = fields.Float('Dist C1')
    dist_c2 = fields.Float('Dist C2')
    dist_c3 = fields.Float('Dist C3')
    reverse = fields.Many2one('fleet.route', string='Reverse route')

    @api.one
    @api.depends('from_loc_id.name', 'to_loc_id.name')
    def _compute_name(self):
        self.name = self.from_loc_id.name + '-' + self.to_loc_id.name

    @api.multi
    def button_create_reverse(self):
        for route in self:
            if not route.reverse:
                new_route = route.copy({'from_loc_id': route.to_loc_id.id,
                                        'to_loc_id': route.from_loc_id.id,
                                        'reverse': route.id})
                route.reverse = new_route


class fleet_card(models.Model):
    _name = 'fleet.card'
    _description = 'Fuel Card'

    name = fields.Char(string='Series card', size=20, required=True)
    type_card = fields.Selection(
        [('2', 'Own pomp'), ('3', 'Rompetrol'), ('4', 'Petrom'), ('5', 'Lukoil'), ('6', 'OMV')], string='Type Card')
    vehicle_ids = fields.Many2many('fleet.vehicle', 'fleet_card_vehicle_rel', 'card_id', 'vehicle_id',
                                   string='Vehicles')
    log_fuel_ids = fields.One2many('fleet.vehicle.log.fuel', 'card_id', string='Fuel log')
    active = fields.Boolean(string='Active', default=1)

    _sql_constraints = [('serie_uniq', 'unique (name)', 'The series must be unique !')]


class fleet_fuel(models.Model):
    _name = 'fleet.fuel'
    _description = 'Fuel'

    name = fields.Char(string='Fuel', size=75, required=True)
    fuel_type = fields.Selection([('gasoline', 'Gasoline'), ('diesel', 'Diesel')], string='Fuel Type')


class fleet_scope(models.Model):
    _name = 'fleet.scope'
    _description = 'Scope'

    name = fields.Char(string='Scope', size=75, required=True)
    categ_id = fields.Many2one('fleet.scope.categ', string='Category')



class fleet_scope_categ(models.Model):
    _name = 'fleet.scope.categ'
    _description = 'Scope'

    name = fields.Char(string='Category',  required=True)


class fleet_division(models.Model):
    _name = 'fleet.division'
    _description = 'Division'

    name = fields.Char(string='Division',  required=True)


class fleet_location(models.Model):
    'Pozitia unei locatii si afisare pozitie pe Google Maps'
    _name = 'fleet.location'
    _description = 'Location'

    name = fields.Char(string='Location', size=100, required=True)
    type = fields.Selection([('0', 'Other'), ('1', 'Partner'), ('2', 'Station')], string='Type')


"""
class fleet_location_type(osv.osv):
    _name = 'fleet.location.type'
    _description = 'Location type'
    
    name = fields.Char(string='Type',  size=100, required=True) 
   
 
"""


class fleet_vehicle_category(models.Model):
    _name = 'fleet.vehicle.category'
    _description = 'Vehicle Category'

    name = fields.Char(string='Category', size=100, required=True)
    code = fields.Char(string='Cod', size=4, required=True)


class fleet_reservoir_level(models.Model):
    _name = 'fleet.reservoir.level'
    _description = 'Fleet Reservoir Level'

    date = fields.Date(string='Date', required=True)
    vehicle_id = fields.Many2one('fleet.vehicle', string='Vehicle', required=True)
    liter = fields.Float('Liter')

    @api.model
    def get_level(self, vehicle_id):
        level = 0.0
        self.env.cr.execute("""SELECT  sum(liter) AS liter
              FROM fleet_vehicle_log_fuel join fleet_vehicle_cost on fleet_vehicle_log_fuel.cost_id = fleet_vehicle_cost.id
              WHERE vehicle_id = %s
           """,
                            (vehicle_id,))
        results = self.env.cr.dictfetchone()
        if results:
            level = results['liter']
            if level is None:
                level = 0
        self.env.cr.execute("""SELECT  sum(norm_cons) AS liter
              FROM fleet_route_log
              WHERE vehicle_id = %s
           """,
                            (vehicle_id,))
        results = self.env.cr.dictfetchone()
        if results and results['liter']:
            level = level - results['liter']

        return level

    @api.model
    def get_level_to(self, vehicle_id, ToDate):
        level = 0.0
        self.env.cr.execute("""SELECT  sum(liter) AS liter
              FROM fleet_vehicle_log_fuel join fleet_vehicle_cost on fleet_vehicle_log_fuel.cost_id = fleet_vehicle_cost.id
              WHERE vehicle_id = %s and
                   date_time <= %s
           """,  (vehicle_id, ToDate,))
        results = self.env.cr.dictfetchone()
        if results and results['liter']:
            level = results['liter']
            if level is None:
                level = 0
        self.env.cr.execute("""SELECT  sum(norm_cons) AS liter
              FROM fleet_route_log
              WHERE vehicle_id = %s  and
                   date_end <= %s
           """, (vehicle_id, ToDate,))
        results = self.env.cr.dictfetchone()
        if results and results['liter']:
            level = level - results['liter']

        return level
