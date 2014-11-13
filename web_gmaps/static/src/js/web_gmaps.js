var map ;

openerp.web_gmaps = function (instance) {

    var QWeb = instance.web.qweb;
    var _t = instance.web._t;
    
    instance.web_gmaps.gmap_marker = instance.web.form.FormWidget.extend({
        template: "gmap_marker",
        init: function (view, code) {
            this._super(view, code);

            var field_lat = code.attrs.lat;
            var field_lng = code.attrs.lng;
            
            this.set({'field_lat':field_lat, 'field_lng':field_lng});

        },
        
        initialize: function() {
            var field_lat = this.get('field_lat');
            var field_lng = this.get('field_lng');  
            var lat = this.field_manager.get_field_value(field_lat);
            var lng = this.field_manager.get_field_value(field_lng); 
            
            var myLatlng = new google.maps.LatLng(lat, lng);
            var mapOptions = {
                zoom: 8,
                center: myLatlng
            };
            
            var div_gmap = this.$el[0];
              

            map = new google.maps.Map(div_gmap, mapOptions);

            var marker = new google.maps.Marker({
                position: myLatlng,
                map: map,
                draggable:false,
            });    
             
            var my_self= this;  
            
            google.maps.event.addListener(marker, 'dragend',function(NewPoint){
                  lat = NewPoint.latLng.lat();
                  lng = NewPoint.latLng.lng();
                  my_self.update_latlng(lat,lng);
               });
               
            this.set({"map": map,"marker":marker});
            
            this.field_manager.on("field_changed:"+field_lat, this, this.display_result);
            this.field_manager.on("field_changed:"+field_lng, this, this.display_result);
        },

        start: function() {
           this.initialize(); 
           var self = this;
           self.on("change:effective_readonly", self, function() {
               marker =  self.get('marker');
               marker.setDraggable(self.get("effective_readonly") ? false : true);
           });
        },
        

        update_latlng: function(lat, lng ){
           var values = {};
           var field_lat = this.get('field_lat');
           var field_lng = this.get('field_lng');  
           values[field_lat] = lat;
           values[field_lng] = lng; 
           this.field_manager.set_values(values).done(function() { });             
        },

        display_result: function() {
          var field_lat = this.get('field_lat');
          var field_lng = this.get('field_lng');  
          var lat = this.field_manager.get_field_value(field_lat);
          var lng = this.field_manager.get_field_value(field_lng);
          map = this.get('map');
          
          var myLatlng = new google.maps.LatLng(lat, lng);
          
          map.setCenter(myLatlng);  
          marker = this.get('marker');
          marker.setPosition(myLatlng);  
        },
        

 
 });

 instance.web.form.custom_widgets.add('gmap_marker', 'instance.web_gmaps.gmap_marker');

 
 instance.web_gmaps.gmap_route = instance.web.form.FormWidget.extend({
        template: "gmap_route",

        init: function (view, code) {
            this._super(view, code);
            var field_from_lat = code.attrs.from_lat;
            var field_from_lng = code.attrs.from_lng;
            var field_to_lat = code.attrs.to_lat;
            var field_to_lng = code.attrs.to_lng; 
            
            var field_distance = code.attrs.distance; 
            var field_duration = code.attrs.duration; 
            
            this.set({'field_from_lat':field_from_lat, 'field_from_lng':field_from_lng, 
                      'field_to_lat':field_to_lat, 'field_to_lng':field_to_lng,
                      'field_distance':field_distance,
                      'field_duration':field_duration}); 
            

        },        
        start: function () {
            var self = this;
            field_from_lat = this.get('field_from_lat');
            field_from_lng =  this.get('field_from_lng');
            field_to_lat =  this.get('field_to_lat');
            field_to_lng = this.get('field_to_lng');
            var from_lat = this.field_manager.get_field_value(field_from_lat);
            var from_lng = this.field_manager.get_field_value(field_from_lng); 
            var to_lat = this.field_manager.get_field_value(field_to_lat);
            var to_lng = this.field_manager.get_field_value(field_to_lng);
                                  
            var div_gmap = this.$el[0];
                        
            var from_Latlng = new google.maps.LatLng(from_lat, from_lng);
            var to_Latlng = new google.maps.LatLng(to_lat, to_lng);
            
            var mapOptions = {
                zoom: 8,
                center: from_Latlng
            };
            
            map = new google.maps.Map(div_gmap,mapOptions);
            
            var directionsService = new google.maps.DirectionsService();
            var directionsDisplay = new google.maps.DirectionsRenderer();
            directionsDisplay.setMap(map);
            
            this.set({"map": map,'directionsDisplay':directionsDisplay, 'directionsService':directionsService}); 
 
 
            this.field_manager.on("field_changed:"+field_from_lat, this, this.display_result);
            this.field_manager.on("field_changed:"+field_from_lng, this, this.display_result);     
            this.field_manager.on("field_changed:"+field_to_lat, this, this.display_result);
            this.field_manager.on("field_changed:"+field_to_lng, this, this.display_result);            
    
           self.on("change:effective_readonly", self, function() {
               var rendererOptions = {
                  draggable: self.get("effective_readonly") ? false : true
               };              
               directionsDisplay.setOptions(rendererOptions);
           }); 
           
           google.maps.event.addListener(directionsDisplay, 'directions_changed', function() {
                if (!self.get("effective_readonly")){
                      self.computeTotal(directionsDisplay.getDirections());
                  }
                
              });
           
           this.display_result(); 
           this.updating = false;    
        },


        display_result: function() {
            
            if (this.updating) return;
            var self = this;
            
            var directionsDisplay = this.get('directionsDisplay');
            var directionsService = this.get('directionsService');
            var from_lat = this.field_manager.get_field_value(this.get('field_from_lat'));
            var from_lng = this.field_manager.get_field_value(this.get('field_from_lng')); 
            var to_lat = this.field_manager.get_field_value(this.get('field_to_lat'));
            var to_lng = this.field_manager.get_field_value(this.get('field_to_lng'));  
            
            if (from_lat==0 | from_lng==0 | to_lat==0 | to_lng==0)
                return;
            var from_Latlng = new google.maps.LatLng(from_lat, from_lng);
            var to_Latlng = new google.maps.LatLng(to_lat, to_lng);         
            var request = {
                  origin:from_Latlng,
                  destination:to_Latlng,
                  travelMode: google.maps.TravelMode.DRIVING
            };
            directionsService.route(request, function(response, status) {
                if (status == google.maps.DirectionsStatus.OK) {
                  directionsDisplay.setDirections(response);
                  if (!self.get("effective_readonly")){
                      self.computeTotal(response);
                  }
                }
            });            
        },
        
        
      computeTotal: function(result) {
          var self = this;
          var distance = 0;
          var duration = 0;
          var myroute = result.routes[0];
          for (var i = 0; i < myroute.legs.length; i++) {
            distance += myroute.legs[i].distance.value;
            duration += myroute.legs[i].duration.value;

          }
          distance = distance / 1000.0;
          duration = duration / 60 / 60;
          var values = {};
          
          
          
          var field_distance = this.get('field_distance');
          var field_duration = this.get('field_duration'); 
          
          values[field_distance] = distance;
          values[field_duration] = duration; 
                   
          var field_from_lat = this.get('field_from_lat');
          var field_from_lng =  this.get('field_from_lng');
          var field_to_lat =  this.get('field_to_lat');
          var field_to_lng = this.get('field_to_lng');
          
          
             
          values[field_from_lat] = result.Lb.origin.lat();
          values[field_from_lng] = result.Lb.origin.lng(); 
          
          values[field_to_lat] = result.Lb.destination.lat();
          values[field_to_lng] = result.Lb.destination.lng();
          
          this.updating = true;
          this.field_manager.set_values(values).done(function() { 
              self.updating = false;
              });   
          
        },


 });
 instance.web.form.custom_widgets.add('gmap_route', 'instance.web_gmaps.gmap_route');

/*
 instance.web_gmaps.gmap_markers = instance.web.View.extend({
    view_loading: function (fv) {
            var attrs = fv.arch.attrs,
            self = this;
            this.fields_view = fv; 
            this.$buttons =   "<div name='CalendarView.buttons' class='oe_calendar_buttons'>";
        },
 });
 
 instance.web.views.add('gmap_markers', 'instance.web_gmaps.gmap_markers');


*/
};



// vim:et fdc=0 fdl=0:
