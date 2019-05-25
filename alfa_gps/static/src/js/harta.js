var map;
var infowindow = new google.maps.InfoWindow();
var geocoder = new google.maps.Geocoder();

var g_marker;
var CarMarkers = [];
var Masini = [];
var ToateMasinile = [];
var pasInterval = 1;

var POI_Markers = [];
var Etape_Markers = [];
var SOS_Markers = [];

var clusterPOI;
var gdir;
var polyline;
var polyline_proc;
var traseuKML;
var Trasee = [];
var newMarkers = [];
var latLngs = [];
var g_editabil = false;
//var progressBar;
var g_date_salvate = false;
var SeIncarca = false;
var requestLinii;
var requestEtape;
var requestLinii_proc;

google.maps.event.addDomListener(window, 'load', init);

function init() {
	var mapDiv = document.getElementById('map_canvas');
	
	var mapTypeIds = [];
	for(var type in google.maps.MapTypeId) {
            mapTypeIds.push(google.maps.MapTypeId[type]);
        }
	mapTypeIds.push("OSM");
	
	
	map = new google.maps.Map(mapDiv, {
		center : new google.maps.LatLng(center_lat, center_lng),
		zoom : zoom_level,
		mapTypeId : google.maps.MapTypeId.ROADMAP,
		mapTypeControlOptions: {
                    mapTypeIds: mapTypeIds
                }
	});
	
	map.mapTypes.set("OSM", new google.maps.ImageMapType({
        getTileUrl: function(coord, zoom) {
            return "http://tile.openstreetmap.org/" + zoom + "/" + coord.x + "/" + coord.y + ".png";
        },
        tileSize: new google.maps.Size(256, 256),
        name: "OpenStreetMap",
        maxZoom: 18
    }));
	 
//	var trafficLayer = new google.maps.TrafficLayer();
//	trafficLayer.setMap(map);
	
	google.maps.event.addListener(map, 'zoom_changed', function() {
		var url = Base_Url + 'index.php/Harta3/zoom/' + map.getZoom();
		downloadUrl(url, function(data) {	});
	});
	google.maps.event.addListener(map, 'center_changed', function() {
		var center = map.getCenter();
		if (isNaN(center.d) == false ) { 
			var url = Base_Url + 'index.php/Harta3/move/' + center.lat() + '/' + center.lng();
			downloadUrl(url, function(data) {	});
		}
	});
	google.maps.visualRefresh = true;
	
	var lineSymbol = {
	  path: google.maps.SymbolPath.FORWARD_CLOSED_ARROW
	};
	
	polyline = new google.maps.Polyline({
		path : [],
		icons: [{
		    icon: lineSymbol,
		    offset: '25%'
		  }],
		strokeColor : "#FF0000",
		strokeOpacity : 0.6,
		strokeWeight : 2
	});

	polyline_proc = new google.maps.Polyline({
		path : [],
		icons: [{
		    icon: lineSymbol,
		    offset: '25%'
		  }],
		strokeColor : "#0000FF",
		strokeOpacity : 0.6,
		strokeWeight : 2
	});

	traseuKML = new google.maps.KmlLayer({ });


	var mcOptions = {
		gridSize : 50,
		maxZoom : 15
	};
	clusterPOI = new MarkerClusterer(map, [], mcOptions);

	if (realtime)
		setInterval('AnimateMasini()', 100);

	showMasini();
	//showSOS();  se face afisarea daca se selecteaza din meniu
}// end init 

function showMasini() {
	if (SeIncarca)
		return;
	// daca viteza internetului e prea mica!
	SeIncarca = true;

	var sidebar = document.getElementById('sidebar');
	sidebar.innerHTML = '<div id="parc"><p>Se încarcă Parc Auto </p></div>';
	ShowLoading();
	ShowStatusMessage('Se încarcă lista de mașini. Așteptați vă rog.');
	var url = Base_Url + "index.php/Functii/last_poz_JSON/" +g_dl_GTM+"/"+g_pl_GTM+"/"+g_idben+'/'+g_col;
	downloadUrl( url, function(data) {
		ShowStatusMessage('Lista de mașini a fost încărcată.');
		HideLoading();
		sidebar.innerHTML = '<div id="parc"><p> Parc Auto </p></div>';
		if (data.responseText == "[]")
			sidebar.innerHTML = '<div id="parc"><p> Nu sunt poziții în intervalul selectat</p></div>';
		var l_Masini = try_eval(data.responseText );
		
		for (var i in l_Masini ) {
			var icon = carIcons[l_Masini[i].Icon] || {};
			var lat = parseFloat(l_Masini[i].lat);
			var lng = parseFloat(l_Masini[i].lng);
			if (isNaN(lat)) lat = 45;
			if (isNaN(lng)) lat = 26;
			var point = new google.maps.LatLng(lat, lng);

			if (Masini[i] != undefined) {
				Masini[i].marker.setPosition(point);
				Masini[i].marker.setIcon(icon.icon);
				Masini[i].marker.setShadow(icon.shadow);
			} else {
				Masini[i] = [];
				var marker = createMarkerCars(point, l_Masini[i].idm, l_Masini[i].Ind, icon);
				Masini[i].marker = marker;
			}
			
			Masini[i].idm = l_Masini[i].idm;
			Masini[i].Col = l_Masini[i].Col;
			Masini[i].Ind = l_Masini[i].Ind;
			Masini[i].Crs = l_Masini[i].Crs;
			Masini[i].Vit = l_Masini[i].Vit;
			Masini[i].Ad1 = l_Masini[i].Ad1;
			Masini[i].Ad2 = l_Masini[i].Ad2;
			Masini[i].Data = l_Masini[i].Data;
			Masini[i].Status = l_Masini[i].Status;
			Masini[i].Sonda_T = l_Masini[i].Sonda_T;
			Masini[i].Sonda_C = l_Masini[i].Sonda_C;
			

			var sidebarEntry = createSidebarEntry(Masini[i].marker, Masini[i].Ind, Masini[i].idm, icon.color, icon.colorShadow, Masini[i].Col);
			var col_sidebar = document.getElementById('sidebar' + Masini[i].Col);
			if (col_sidebar == undefined) {
				col_sidebar = document.createElement('sidebar' + Masini[i].Col);
				col_sidebar.id = 'sidebar' + Masini[i].Col;
				col_sidebar.innerHTML = '<br> - ' + Masini[i].Col + ' -';
				sidebar.appendChild(col_sidebar);
			}

			col_sidebar.appendChild(sidebarEntry);

		}
		SeIncarca = false;
	});

}

function createMarkerCars(point, idm, Ind, icon) {
	var marker = new google.maps.Marker({
		map : map,
		position : point,
		title : Ind,
		icon : icon.icon,
		shadow : icon.shadow
	});
	google.maps.event.addListener(marker, "click", function() {
		detaliiMasina(idm, false, true);
	});
	return marker;
}

function detaliiMasina(idm, cu_balon, pan_to) {

	if (Masini[idm] == undefined)
		return;

	var html = "<table>" +
			   "<tr><td><b>Mașina:</b></td>  <td> " + Masini[idm].Ind + " </td> </tr>" + 
			//   "<tr><td><b>Id intern:</b></td>  <td> " + idm + " </td> </tr>" +
			   "</table>";

	// eliminare Linii desenate de la alta masina
	if (g_idm != idm) {
		if (polyline != undefined) {
			polyline.setPath([]);
		}
		if (polyline_proc != undefined) {
			polyline_proc.setPath([]);
		}
		// elimin punctle vechi
		for (var i in Etape_Markers ) {
			if (Etape_Markers[i] != undefined) {
				Etape_Markers[i].setMap(null);
			}
		}

		var div = document.getElementById("car" + g_idm);
		if (div != undefined)
			div.innerHTML = "<i>" + Masini[g_idm].Ind + "</i>";
		g_idm = idm;

	}
	var div = document.getElementById("car" + idm);
	if (div != undefined)
		div.innerHTML = "<b>" + Masini[idm].Ind + "</b>";

	//showLinii(1);

	if (cu_balon) {
		infowindow.setContent(html);
		infowindow.open(map, Masini[idm].marker);
	}
	if (pan_to)
		var latlng = Masini[idm].marker.getPosition();
		if (isNaN(latlng.d) == false ) map.panTo(latlng);

	// ===== Check to see if this browser claims to support <canvas> ===
	if (document.getElementById('carcanvas').getContext) {
		canvas = document.getElementById("carcanvas").getContext('2d');
		rotatecar(Masini[idm].Crs * Math.PI / 180, canvas);
	}

	var div = document.getElementById("indicativ");
	div.innerHTML = Masini[idm].Ind;
	var div = document.getElementById("DataP");
	div.innerHTML = Masini[idm].Data;
	var div = document.getElementById("Viteza");
	div.innerHTML = Masini[idm].Vit + " km/h";
	var div = document.getElementById("Directia");
	if (div != undefined)
		div.innerHTML = Masini[idm].Crs;
	var div = document.getElementById("Temperatura");
	var divLabel = document.getElementById("LabelTemperatura");
	var divMenu = document.getElementById("Menu_Temp");
	if (Masini[idm].Sonda_T == 1) {
		div.innerHTML = '';
		divLabel.innerHTML = '<strong>Temperatură</strong>';
		div.innerHTML = Masini[idm].Ad1;
		div.visible = true;
		divLabel.visible = true;
		divMenu.visible = true;
	} else {
		div.innerHTML = '';
		divLabel.innerHTML = '';
		div.visible = false;
		divLabel.visible = false;
		divMenu.visible = 'hidden';
	}
	/*
	var div = document.getElementById("Carburant");
	var divLabel = document.getElementById("LabelCarburant");
	var divMenu = document.getElementById("Menu_Carb");
	if (Masini[idm].Sonda_C == 1){
	div.innerHTML  = '';
	divLabel.innerHTML  = '<strong>Carburant</strong>';
	div.innerHTML = Masini[idm].Ad2;
	div.visible = true;
	divLabel.visible = true;
	divMenu.visible = true;
	}
	else {
	div.innerHTML  = '';
	divLabel.innerHTML  = '';
	div.visible = false;
	divLabel.visible = false;
	divMenu.visible = false;
	}
	*/

	//var div = document.getElementById("Latitudine");
	///	if (div != undefined ) div.innerHTML = masini[idm].marker.getLatLng().lat() ;
	//	var div = document.getElementById("Longitudine");
	//	if (div != undefined ) div.innerHTML = masini[idm].marker.getLatLng().lng() ;

	var div = document.getElementById("Status");
	if (div != undefined)
		div.innerHTML = Masini[idm].Status;
	var div = document.getElementById("Adresa");
	if (div != undefined) {
		div.innerHTML = '';
		var URL = Base_Url + "index.php/Functii/GetAdress/" + Masini[idm].marker.getPosition().lat() + '/' + Masini[idm].marker.getPosition().lng()+'/'+g_idben;
		downloadUrl(URL, function(data) {	div.innerHTML = data.responseText;	});
	}

}

function createSidebarEntry(marker, name, idm, color, colorShadow, Col) {

	var div = document.createElement('div');
	if (idm == g_idm)
		var html = '<b>' + name + '</b>';
	else
		var html = '<i>' + name + '</i>';
	div.id = 'car' + idm;
	div.innerHTML = html;
	div.style.cursor = 'pointer';
	div.style.marginBottom = '5px';
	div.style.textShadow = "2px 2px 4px " + colorShadow;
	div.style.color = color;


 

	google.maps.event.addDomListener(div, "click", function() {
		detaliiMasina(idm, true, true);
		showLinii();
		//showLinii_proc();
		//showEtape();
		showTraseu();
	});
	



	
	google.maps.event.addDomListener(div, 'mouseover', function() {
		div.style.backgroundColor = '#eee';
	});
	google.maps.event.addDomListener(div, 'mouseout', function() {
		div.style.backgroundColor = '#FFFFE8';
	});
	return div;
}
//////////////////////////////////////////////////////////////////////////////

function showTraseu() {

    if (traseuKML != undefined) {
 		traseuKML.setMap();
 	} 
  
	var url = Base_Url + "index.php/Functii/GetKML/" + g_idm +'/'+g_dl_GTM+"/"+g_pl_GTM+"/" ;
	
	traseuKML.setUrl(url);
	traseuKML.setMap(map);	
}

//////////////////////////////////////////////////////////////////////////////

function showLinii() {
    
    if (requestLinii != undefined) {
 		requestLinii.abort();
 	} 	
    
	var url = Base_Url + "index.php/Functii/Line_JSON/" +g_dl_GTM+"/"+g_pl_GTM+"/" + g_idm;
	ShowLoading();
	ShowStatusMessage('Se încarcă traseul. Așteptați vă rog.');
	requestLinii = downloadUrl(url, function(data) {
		var puncte = try_eval(data.responseText);
		var path = [];
		for (var i in puncte ) {
			path[i] = new google.maps.LatLng(puncte[i][0], puncte[i][1]);
		}

		polyline.setPath(path);
		polyline.setMap(map);

		ShowStatusMessage('Traseul a fost încărcat');
		HideLoading();
	});

}

function showLinii_proc(procesare) {
    
    if (requestLinii_proc != undefined) {
 		requestLinii_proc.abort();
 	} 

	if(typeof(procesare)==='undefined') procesare = 0;
	var url = Base_Url + "index.php/Functii/Line_proc_JSON/" +g_dl_GTM+"/"+g_pl_GTM+"/" + g_idm+"/"+procesare;
	ShowLoading();
	ShowStatusMessage('Se încarcă traseul procesat. Așteptați vă rog.');
	requestLinii_proc = downloadUrl(url, function(data) {
	// TODO: De facut un array cu trasee
		var cale = try_eval(data.responseText);
		var path = [];
		for (var c in cale){
			var puncte = try_eval(cale[c]);
			for (var i in puncte ) {
				path.push( new google.maps.LatLng(puncte[i][1], puncte[i][0]));
			}
		}

		polyline_proc.setPath(path);
		polyline_proc.setMap(map);

		ShowStatusMessage('Traseul a fost încărcat procesat');
		HideLoading();
	});

}


/////// se extimeaza urmatoarul punct in cazul in care masina este in miscare;
function AnimateMasini() {
	if (SeIncarca)
		return;
	// daca viteza internetului e prea mica!
	pasInterval++;
	if (pasInterval == RataRefresh) {
		pasInterval = 1;
		showMasini();
		return;
	}

	// animare masini
	// calculare pozitie noua
	//for (var i = 0; i < masini.length; i++) {
	for (var i in Masini ) {
		if (Masini[i].Vit > 0) {
			dist = Masini[i].Vit / 36000;
			var newpoz = calcLatLng(Masini[i].marker.getPosition(), Masini[i].Crs, dist);
			Masini[i].marker.setPosition(newpoz);
		}
	}

}


function showSOS(){
	var url = Base_Url + "index.php/Functii/GetSOS/" + g_dl_GTM + "/" + g_pl_GTM + "/" + g_idben + '/' + g_col;	
	ShowStatusMessage('Se încarcă SOSuri. Așteptați vă rog.');
	ShowLoading();

	// elimin punctle vechi
	for (var i in SOS_Markers ) {
		if (SOS_Markers[i] != undefined) {
			SOS_Markers[i].setMap(null);
		}
	}
	SOS_Markers = [];
	downloadUrl(url, function(data) {
		ShowStatusMessage('SOSurile au fost încărcate.');
		HideLoading();
		var sosuri = try_eval(data.responseText);
		for (var i in sosuri) {
			var point = new google.maps.LatLng(sosuri[i].Lat, sosuri[i].Lng);
			var html = "<table>" + 
					   "<tr><td><b>Mașina:</b></td><td>" + sosuri[i].Ind+	 "</td> </tr> "  +
					   "<tr><td><b>Data:</b></td><td>" + sosuri[i].DP+	 "</td> </tr> "  +
					   "</table>";
			var marker = createMarkerStep(point, html, Icon_SOS);
			SOS_Markers[i] = marker;
			marker.setMap(map);
		}
	});
}


function showEtape() {
 	
 	if (requestEtape != undefined) {
 		requestEtape.abort();
 	} 	 
 
 
	var url = Base_Url + "index.php/Functii/etape_JSON/" +g_dl_GTM+"/"+g_pl_GTM+"/" + g_idm;
	ShowStatusMessage('Se încarcă etape traseu. Așteptați vă rog.');
	ShowLoading();

	// elimin punctle vechi
	for (var i in Etape_Markers ) {
		if (Etape_Markers[i] != undefined) {
			Etape_Markers[i].setMap(null);
		}
	}
	Etape_Markers = [];
	requestEtape = downloadUrl(url, function(data) {
		ShowStatusMessage('Etapele au fost încărcate.');
		HideLoading();
		var etape = try_eval(data.responseText);

		var distTot = 0;
		for (var i in etape) {
			var point = new google.maps.LatLng(etape[i].Lat, etape[i].Lng);

			if (i == 0) {
				var icon = etapeIcons.Start;
			} else if (i == etape.length - 1) {
				var icon = etapeIcons.End;
			} else {
				var icon = etapeIcons.Node;
			}

			distTot = distTot + parseFloat(etape[i].Dist);
			distTot = Math.round(distTot * 10) / 10;
			var Tst = Math.round(etape[i].Tst * 10) / 10;
			var html = "<table>" + "<tr><td><b>Etapa:</b></td><td>" + etape[i].Id +	 "</td> </tr>" + 
								   "<tr><td><b>Data:</b></td>  <td>" + etape[i].Data +  "</td> </tr>" +
								   "<tr><td><b>Viteza max:</b></td>  <td>" + etape[i].VitMax +  " km/h </td> </tr>" + 
								   "<tr><td><b>Distanță etapă:</b></td>  <td>" + etape[i].Dist + " km </td> </tr>" + 
								   "<tr><td><b>Distanța totală:</b></td>  <td>" + distTot + " km </td> </tr>" + 
								   "<tr><td><b>Timp Staționare:</b></td>  <td>" + Tst + " min </td> </tr>";

			var marker = createMarkerStep(point, html, icon);

			Etape_Markers[i] = marker;
			marker.setMap(map);
		}

	});
}

function createMarkerStep(point, html, icon) {
	var l_html = html;
	var marker = new google.maps.Marker({
		map : map,
		position : point,
		icon : icon.icon,
		shadow : icon.shadow
	});

	geocoder.geocode({
		'latLng' : point
	}, function(results, status) {
		if (status == google.maps.GeocoderStatus.OK) {
			if (results[0]) {
				place = results[0].formatted_address;
				l_html = html + "<tr><td><b>Adresa:</b></td>  <td> " + place + "</td> </tr>";
			}
		}
	});

	google.maps.event.addListener(marker, "click", function() {
		infowindow.setContent(l_html);
		infowindow.open(map, marker);
	});

	return marker;
}



/////////////////////////////////////////////////////////////////////////////////

function showPOIs() {
	var url = Base_Url + "index.php/POI/GetPOIs/"+g_idben;
	ShowStatusMessage('Se încarcă POIuri. Așteptați vă rog.');
	ShowLoading();
	var marker, markersArray = [];

	POI_Markers = [];

	clusterPOI.clearMarkers();

	downloadUrl(url, function(data) {
		ShowStatusMessage('POI-urile au fost încărcate.');
		HideLoading();
		if (data.responseText != 'eroare') {
			json = try_eval(data.responseText );
			var j = POI_Markers.length;
			for (var i in json ) {

				var opt = {
					//icon : 'http://labs.google.com/ridefinder/images/mm_20_red.png',
					title : json[i].Nme,
					draggable : g_editabil
				};
				var point = new google.maps.LatLng(parseFloat(json[i].lat), parseFloat(json[i].lng));
				var icon = poiIcons[json[i].typ] || {};
				marker = createMarkerPOI(point, opt,icon, json[i].POI);
				markersArray.push(marker);
				var mjson = {
					"Nme" : json[i].Nme,
					"Fma" : json[i].Fma,
					"cFma": json[i].cFma,
					"Adr" : json[i].Adr,
					"Prior" : json[i].Prior,
					"POI" : json[i].POI,
					'typ': json[i].typ
				};
				POI_Markers[json[i].POI] = mjson;

				//map.addOverlay(POI_Markers[j+i].marker);
			}
			clusterPOI.addMarkers(markersArray);
			//clusterPOI.fitMapToMarkers();
		} else
			ShowStatusMessage('Eroare la încarcare POIuri.');
	});
}

function createMarkerPOI(point, opt, icon, poz) {
	var l_adr = '';
	var html;
	var marker = new google.maps.Marker({
		map : map,
		position : point,
		icon : icon.icon,
		shadow: icon.shadow ,
		title : opt.title,
		draggable : opt.draggable
	});

	/*
	 geocoder.getLocations(point, function (response) {
	 if (!(!response || response.Status.code != 200)) {
	 place = response.Placemark[0];
	 l_adr =  place.address  ;
	 }
	 });    */
	google.maps.event.addListener(marker, 'click', function() {
		clickPOI(marker, poz);
	});

	google.maps.event.addListener(marker, 'dragend', function(NewPoint) {
		/*	geocoder.getLocations(NewPoint, function (response) {
		 if (!(!response || response.Status.code != 200)) {
		 place = response.Placemark[0];
		 l_adr =  place.address ;
		 }
		 });   */
	});

	return marker;

}

function clickPOI(marker, poz) {

	g_marker = marker;
	// setez variabila globala

	var Nme = POI_Markers[poz].Nme;
	var Fma = POI_Markers[poz].Fma;
	var cFma = POI_Markers[poz].cFma;
	var Adr = POI_Markers[poz].Adr;
	var Prior = POI_Markers[poz].Prior;
	var POI = POI_Markers[poz].POI;
	var typ = POI_Markers[poz].typ;
//'albastru','rosu','verde','bleu','galben','mov','violet'
	if (g_editabil) {
		html = "<table>" + 
		"<tr><td><b>Nume:</b></td><td><input type='text' id='Nme' value='"  + Nme + "'/></td> </tr>" +
	    "<tr><td><b>Firma:</b></td><td><input type='text' id='Fma' value='" + Fma + "'/></td> </tr>" +
	    "<tr><td><b>Cod Firma:</b></td> <td><input type='text' id='cFma' value='" + cFma + "'/></td> </tr>" + 
	    "<tr><td><b>Adresa:</b></td> <td><input type='text' id='Adr' value='" + Adr + "'/></td> </tr>" +
	    "<tr><td><b>Prioritatea:</b></td> <td><input type='text' id='Prior' value='" + Prior + "'/></td></tr>" + 
	    "<tr><td><b>Tipul: </b></td>   <td><input list='tipuri' type='text' id='typ' value='" + typ + "'/></td></tr>" + 
	    
	    "   <datalist id='tipuri'> " +
  		"		<option value='albastru'> "+
  		"		<option value='rosu'> "+
  		"		<option value='verde'> "+
  		"		<option value='bleu'> "+  
  		"		<option value='galben'> "+
  		"		<option value='mov'> "+
  		"		<option value='violet'> "+  
		"	</datalist> " +
	    
	    "<tr><td><b>id POI:</b></td> <td><input type='text' id='POI' readonly='readonly' value='" + POI + "'/></td></tr>" + 
	    "<tr><td></td><td><input type='button' value='Salvează' onclick='saveData(" + poz+ ")'/></td></tr>";
	} else {
		//if (Adr=="") {Adr = l_adr;}
		html = "<table>" + "<tr><td><b>Nume:</b></td>  <td>" + Nme + "</td> </tr>";
		if (Fma != "") {
			html = html + "<tr><td><b>Firma:</b></td> <td>" + Fma + "</td> </tr>";
		}
		if (cFma != "") {
			html = html + "<tr><td><b>Cod Firma:</b></td> <td>" + cFma + "</td> </tr>";
		}
		if (Adr != "") {
			html = html + "<tr><td><b>Adresa:</b></td> <td>" + Adr + "</td> </tr>";
		}
		//	"<tr><td>Prioritatea:</td> <td>"+Prior+"</td> </tr>" +
		//	"<tr><td>id POI:</td> <td>"+POI+"</td></tr>" ;
	}
	//if (l_adr!=''){html = html + '<br> <b>Adresa:</b>' + l_adr + '<br>';}
	infowindow.setContent(html);
	infowindow.open(map, marker);
}

function saveData(poz) {

	ShowStatusMessage('Salvare date.');
	ShowLoading();

	POI_Markers[poz].Nme = document.getElementById("Nme").value;
	POI_Markers[poz].Fma = document.getElementById("Fma").value;
	POI_Markers[poz].cFma = document.getElementById("cFma").value;
	POI_Markers[poz].Adr = document.getElementById("Adr").value;
	POI_Markers[poz].Prior = document.getElementById("Prior").value;
	POI_Markers[poz].POI = document.getElementById("POI").value;
	POI_Markers[poz].typ = document.getElementById("typ").value;

	if (POI_Markers[poz].Nme == '')
		POI_Markers[poz].Nme = 'null';
	if (POI_Markers[poz].Fma == '')
		POI_Markers[poz].Fma = 'null';
	if (POI_Markers[poz].cFma == '')
		POI_Markers[poz].cFma = 'null';
	if (POI_Markers[poz].Adr == '')
		POI_Markers[poz].Adr = 'null';
	if (POI_Markers[poz].Prior == '')
		POI_Markers[poz].Prior = 'null';
	if (POI_Markers[poz].POI == '')
		POI_Markers[poz].POI = 'null';

	var latlng = g_marker.getPosition();
	var lat = latlng.lat();
	var lng = latlng.lng();

	var url = Base_Url + "index.php/POI/POI_save/" + g_idben +'/' + encodeURI(POI_Markers[poz].Nme) + "/" +
													  encodeURI(POI_Markers[poz].Fma) + "/" +
													  encodeURI(POI_Markers[poz].cFma) + "/" +
													  encodeURI(POI_Markers[poz].Adr) + "/" +
													   POI_Markers[poz].Prior + "/" +
													   POI_Markers[poz].POI + "/" + lat + "/" + lng+ "/"+ POI_Markers[poz].typ  ;

	//var url = encodeURI(url);

	downloadUrl(url, function(data, responseCode) {
		infowindow.close();
		HideLoading();
		if (responseCode == 200) {
			POI_Markers[poz].POI = decodeURI(data.responseText);
			HideLoading();
			ShowStatusMessage("Locația a fost salvată.");
			g_date_salvate = true;
			var icon = poiIcons[POI_Markers[poz].typ];
			g_marker.setIcon(icon.icon);
		} else {
			infowindow.setContent(data.responseText);
			infowindow.open(map, g_marker);
		}

	});
}

function addPOI() {

	if (!g_editabil)
		return;

	var marker;
	var dog = true;
	var noMore = false;
	i = POI_Markers.length;
	i = 9999999
	// idul POI-ului nu e in regula
	var mjson = {
		"Nme" : 'x',
		"Fma" : 'x',
		"cFma" : 'x',
		"Adr" : 'x',
		"Prior" : 'x',
		"POI" : 'null'
	};

	POI_Markers[9999999] = mjson;
	//POI_Markers.push(mjson);

	var point = map.getCenter();
	var icon = poiIcons['rosu'] || {};
	var opt = {
		//icon : 'http://labs.google.com/ridefinder/images/mm_20_red.png',
		title : 'POI nou',
		draggable : true
	};

	 
	marker = createMarkerPOI(point, opt, icon, i);
	//marker = showPOI(point, opt, i);

	POI_Markers[i].marker = marker;

	clusterPOI.addMarker(marker);

}

////-----------------------------------------------------------------------------

function ShowStatusMessage(message) {
	document.getElementById("statusMessage").innerHTML = message;
	window.status = message;
}

function ShowLoading() {
	document.getElementById("loading").style.visibility = 'visible';
}

function HideLoading() {
	document.getElementById("loading").style.visibility = 'hidden';
}

function calcLatLng(latlng, brng, dist) {
	var lat1 = latlng.lat() * Math.PI / 180;
	var lng1 = latlng.lng() * Math.PI / 180;
	var dist = parseFloat(dist / 6371);
	var brng = brng * Math.PI / 180;

	var lat2 = Math.asin(Math.sin(lat1) * Math.cos(dist) + Math.cos(lat1) * Math.sin(dist) * Math.cos(brng));
	var lng2 = lng1 + Math.atan2(Math.sin(brng) * Math.sin(dist) * Math.cos(lat1), Math.cos(dist) - Math.sin(lat1) * Math.sin(lat2));
	lng2 = (lng2 + 3 * Math.PI) % (2 * Math.PI) - Math.PI;
	// normalise to -180...+180

	lat2 = lat2 * 180 / Math.PI;
	lng2 = lng2 * 180 / Math.PI;
	return new google.maps.LatLng(lat2, lng2);
}

function downloadUrl(url, callback) {
	var request = window.ActiveXObject ? new ActiveXObject('Microsoft.XMLHTTP') : new XMLHttpRequest;

	request.onreadystatechange = function() {
		if (request.readyState == 4) {
			request.onreadystatechange = doNothing;
			callback(request, request.status);
		}
	};

	request.open('GET', url, true);
	request.send(null);
	return request;
}

function try_eval(text){
	var rez ;
	if (text == '') text = '[]';
	try {
		rez = eval('('+ text+ ')');
	}
	catch(err){
	  document.location.reload();
	  txt="Eroare in pagina.\n\n";
	  txt+= text;
	  txt+="\n\nDescriere eroare: " + err.message + "\n\n";
	  txt+="Click OK to continue.\n\n";
	  alert(txt);	
	  rez = [];
	}
	return rez;
}

function doNothing() {
}

function editabilPOI() {
	g_editabil = !g_editabil;
	var div = document.getElementById("editabilPOI");
	if (g_editabil)
		div.innerHTML = "<b>" + div.text + "</b>";
	else
		div.innerHTML = div.text;
	showPOIs();
}
