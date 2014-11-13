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



from datetime import datetime, timedelta, date
from openerp.osv import fields, osv
import time
import pytz
from openerp import tools
import openerp.addons.decimal_precision as dp
from libxslt import timestamp
import math
from openerp.tools.translate import _

def str_to_datetime(strdate):
    return datetime.datetime.strptime(strdate, tools.DEFAULT_SERVER_DATE_FORMAT)



class fleet_vehicle_doc(osv.Model):
    _name = 'fleet.vehicle.doc'
    _description = 'Fleet Vehicle Document'


    def compute_next_year_date(self, strdate):
        oneyear = datetime.timedelta(days=365)
        curdate = str_to_datetime(strdate)
        return datetime.datetime.strftime(curdate + oneyear, tools.DEFAULT_SERVER_DATE_FORMAT)


    def get_days_left(self, cr, uid, ids, prop, unknow_none, context=None):
        """return a dict with as value for each contract an integer
        if contract is in an open state and is overdue, return 0
        if contract is in a closed state, return -1
        otherwise return the number of days before the contract expires
        """
        res = {}
        for record in self.browse(cr, uid, ids, context=context):
            if (record.expiration_date and (record.state == 'open' or record.state == 'toclose')):
                today = str_to_datetime(time.strftime(tools.DEFAULT_SERVER_DATE_FORMAT))
                renew_date = str_to_datetime(record.expiration_date)
                diff_time = (renew_date-today).days
                res[record.id] = diff_time > 0 and diff_time or 0
            else:
                res[record.id] = -1
        return res

    _order='state desc,expiration_date'
    
    _columns = {      
        'vehicle_id':   fields.many2one('fleet.vehicle', 'Vehicle', required=True),
        'name':         fields.char('Document',  size=100, required=True),  
        'start_date':   fields.date('Document Start Date', help='Date when the coverage of the documents begins'),
        'expiration_date': fields.date('Document Expiration Date', help='Date when the coverage of the documents expirates (by default, one year after begin date)'),
        'days_left': fields.function(get_days_left, type='integer', string='Warning Date'),
        'state': fields.selection([('open', 'In Progress'), ('toclose','To Close'), ('closed', 'Terminated')], 'Status', readonly=True, help='Choose wheter the document is still valid or not'),                
    } 

    _defaults = {
        'start_date': fields.date.context_today,
        'state':'open',
        'expiration_date': lambda self, cr, uid, ctx: self.compute_next_year_date(fields.date.context_today(self, cr, uid, context=ctx)),
    }
  
   
fleet_vehicle_doc()



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: