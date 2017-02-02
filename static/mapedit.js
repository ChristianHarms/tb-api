

function initMap() {
    var markers = [];
    var myLatLng = {lat: 51, lng: 8};
    var map = new google.maps.Map(document.getElementById('map'), {
        zoom: 7,
        center: myLatLng
    });

    //https://developers.google.com/maps/documentation/javascript/infowindows
    var infowindow = new google.maps.InfoWindow({
        content: ''
    });

    //http://www.movable-type.co.uk/scripts/latlong.html
    function distance(lat1, lon1, lat2, lon2) {
        var R = 6371e3; // metres
        var φ1 = lat1;
        var φ2 = lat2;
        var Δφ = (lat2-lat1);
        var Δλ = (lon2-lon1);

        var a = Math.sin(Δφ/2) * Math.sin(Δφ/2) +
            Math.cos(φ1) * Math.cos(φ2) *
            Math.sin(Δλ/2) * Math.sin(Δλ/2);
        var c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));

        return R * c;
    }

    function onMap(lat, long) {
        var skip = false;
        for (var j=0; j<markers.length; j++) {
            var dist = distance(markers[j].position.lat(),markers[j].position.lng(), lat, long);
            console.log(dist);
            if (!skip && dist<100) {
                markers[j].count++;
                return true;
            }
        }
        return false;
    }
    //create all known locations as marker http://kml4earth.appspot.com/icons.html
    for (i=0; i<MAPDATA.locations.length; i++) {
        var config = MAPDATA.locations[i];
        console.log(config);
        if (config.home) {
            icon = "//maps.google.com/mapfiles/kml/pal2/icon10.png";
        } else {
            if (config.work) {
                icon = "//maps.google.com/mapfiles/kml/pal2/icon60.png"
            } else {
                icon = "//maps.google.com/mapfiles/kml/pal2/icon28.png"
            }
        }
        var marker = new google.maps.Marker({
            position: new google.maps.LatLng(config.pos.lat, config.pos.long),
            map: map,
            icon: "//maps.google.com/mapfiles/kml/pal2/icon10.png",
            animation: google.maps.Animation.DROP,
            count: 1,
            title: config.name
        });
        markers.push(marker);
    }

    //add all geofancy points
    for (var i=0; i<MAPDATA.geofancy.length; i++) {
        var config = MAPDATA.geofancy[i];
        if (config.pos && config.pos.long && config.pos.lat) {
            //find other marker with the same position
            if (!onMap(config.pos.lat, config.pos.long)) {
                console.log(config);
                var marker = new google.maps.Marker({
                    position: new google.maps.LatLng(config.pos.lat, config.pos.long),
                    map: map,
                    count: 1,
                    draggable: true,
                    title: config.name
                });

                marker.addListener('click', function() {
                    infowindow.close();
                    console.log(infowindow);
                    infowindow.setContent('<h4>Diesen Marker als Ort speichern?</h4>'+
                        'Name: "'+this.title+'", '+this.count+'x logs' +
                        '<form method="POST" action="/mapedit">'+
                        '<input type="hidden" name="name" value="'+this.title+'" />'+
                        '<input type="hidden" name="lat" value="'+this.position.lat()+'" />'+
                        '<input type="hidden" name="lng" value="'+this.position.lng()+'" />'+
                        '<input type="submit" value="Speichern" />'+
                        '</form>');

                    infowindow.open(map, this);
                });
                markers.push(marker);
            }
        }
    }


    var bounds = new google.maps.LatLngBounds();
    for (var i = 0; i < markers.length; i++) {
        bounds.extend(markers[i].getPosition());
    }

    map.fitBounds(bounds);
}