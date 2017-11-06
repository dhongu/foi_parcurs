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


from odoo import models, fields, api, _
from lxml import etree
from odoo.exceptions import UserError

import urllib
import urllib2

try:
    import json
except ImportError:
    import simplejson as json


def fetch_json(query_url, params={}, headers={}):
    """Retrieve a JSON object from a (parameterized) URL.
    
    :param query_url: The base URL to query
    :type query_url: string
    :param params: Dictionary mapping (string) query parameters to values
    :type params: dict
    :param headers: Dictionary giving (string) HTTP headers and values
    :type headers: dict 
    :return: A `(url, json_obj)` tuple, where `url` is the final,
    parameterized, encoded URL fetched, and `json_obj` is the data 
    fetched from that URL as a JSON-format object. 
    :rtype: (string, dict or array)
    
    """
    encoded_params = urllib.urlencode(params)
    url = query_url + encoded_params
    request = urllib2.Request(url, headers=headers)
    response = urllib2.urlopen(request)
    return (url, json.load(response))


def get_url(url):
    """Return a string of a get url query"""
    try:
        import urllib

        objfile = urllib.urlopen(url)
        rawfile = objfile.read()
        objfile.close()
        return rawfile
    except ImportError:
        raise UserError('Unable to import urllib !')
    except IOError:
        raise UserError('Web Service does not exist !')


class GoogleMaps(object):
    _DIRECTIONS_QUERY_URL = 'http://maps.googleapis.com/maps/api/directions/json?'

    def __init__(self, referrer_url=''):
        self.referrer_url = referrer_url

    def directions(self, origin, destination, mode='driving', **kwargs):
        """
        Get directions from `origin` to `destination`.
        """
        params = {
            'origin': origin,
            'destination': destination,
            'sensor': 'false',
            'mode': mode,
        }
        params.update(kwargs)
        if mode == 'transit':
            if not params.get('departure_time') and not params.get('arrival_time'):
                params['mode'] = 'driving'
        url, response = fetch_json(self._DIRECTIONS_QUERY_URL, params=params)
        status_code = response['status']
        if status_code != 'OK':
            raise UserError(_('Impossible to access data'))
        return response

    def duration(self, origin, destination, mode='driving', **kwargs):
        response = self.directions(origin, destination, mode, **kwargs)
        duration = 0
        routes = response.get('routes')
        if routes:
            legs = routes[0].get('legs')
            if legs:
                duration = legs[0].get('duration', {}).get('value', 0)
        return duration

    def distance(self, origin, destination, mode='driving', **kwargs):
        response = self.directions(origin, destination, mode, **kwargs)
        distance = 0
        routes = response.get('routes')
        if routes:
            legs = routes[0].get('legs')
            if legs:
                distance = legs[0].get('distance', {}).get('value', 0)
        return distance


class fleet_location(models.Model):
    _inherit = 'fleet.location'
    'Pozitia unei locatii si afisare pozitie pe Google Maps'

    lat = fields.Float('Latitude', digits=(9, 6))
    lng = fields.Float('Longitude', digits=(9, 6))
    radius = fields.Float('Radius', default=1.0)  # raza in km sau metri

    @api.multi
    def action_get_lat_lng(self):
        for loc in self:
            url = 'http://maps.googleapis.com/maps/api/geocode/xml?address=' + urllib.quote(loc.name)
            rawfile = get_url(url)
            dom = etree.fromstring(rawfile)
            try:
                lat = dom.xpath('//location/lat')[0].text
                lng = dom.xpath('//location/lng')[0].text
                loc.write({'lat': lat, 'lng': lng})
            except:
                print url
                raise UserError('Unable to get location !')

class fleet_route(models.Model):
    _inherit = 'fleet.route'

    from_lat = fields.Float(related='from_loc_id.lat', digits=(9, 6), string="Latitude from")
    from_lng = fields.Float(related='from_loc_id.lng', digits=(9, 6), string="Longitude from")
    to_lat = fields.Float(related='to_loc_id.lat', digits=(9, 6), string="Latitude to")
    to_lng = fields.Float(related='to_loc_id.lng', digits=(9, 6), string="Longitude to")

    # todo: add via  in care sa fie mai multe puncte
    # de adaugat un KML

    @api.multi
    def action_get_distance_duration(self):
        for route in self:

            url = 'http://maps.googleapis.com/maps/api/directions/xml?'
            params = {
                'origin': route.from_loc_id.name,
                'destination': route.to_loc_id.name,
                'sensor': 'false',
                'mode': 'driving',
            }
            if route.from_lat and route.from_lng:
                params['origin'] = str(route.from_lat) + ',' + str(route.from_lng)
            if route.to_lat and route.to_lng:
                params['destination'] = str(route.to_lat) + ',' + str(route.to_lng)

            encoded_params = urllib.urlencode(params)
            url = url + encoded_params
            rawfile = get_url(url)
            dom = etree.fromstring(rawfile)
            status = dom.xpath('//DirectionsResponse/status')[0].text
            if status == 'OK':
                duration = float(dom.xpath('/DirectionsResponse/route/leg/duration/value')[0].text) / 60 / 60
                distance = float(dom.xpath('/DirectionsResponse/route/leg/distance/value')[0].text) / 1000
                route.write({'duration': duration, 'distance': distance})
