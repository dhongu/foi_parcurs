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


import time
from openerp.report import report_sxw
from openerp.osv import osv
from openerp import pooler
 



class map_sheet(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(map_sheet, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
        })



        
    
class report_map_sheet(osv.AbstractModel):
    _name = 'report.alfa_fleet.report_map_sheet'
    _inherit = 'report.abstract_report'
    _template = 'alfa_fleet.report_map_sheet'
    _wrapped_report_class = map_sheet

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:


