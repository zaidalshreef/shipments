let originMap;
let originMarker;
let destinationMap;
let destinationMarker;

function initMaps() {
    const origin = {
        lat: parseFloat(document.getElementById('ship_from_lat').value),
        lng: parseFloat(document.getElementById('ship_from_lng').value)
    };
    const destination = {
        lat: parseFloat(document.getElementById('ship_to_lat').value),
        lng: parseFloat(document.getElementById('ship_to_lng').value)
    };

     originMap = new google.maps.Map(document.getElementById('originMap'), {
        center: origin,
        zoom: 12
    });

     destinationMap = new google.maps.Map(document.getElementById('destinationMap'), {
        center: destination,
        zoom: 12
    });


    originMarker = new google.maps.Marker({
        position: origin,
        map: originMap,
        draggable: false
    });

    destinationMarker = new google.maps.Marker({
        position: destination,
        map: destinationMap,
        draggable: false
    });

    originMarker.addListener('dragend', function(event) {
        document.getElementById('ship_from_lat').value = event.latLng.lat();
        document.getElementById('ship_from_lng').value = event.latLng.lng();
    });

    destinationMarker.addListener('dragend', function(event) {
        document.getElementById('ship_to_lat').value = event.latLng.lat();
        document.getElementById('ship_to_lng').value = event.latLng.lng();
    });

    const originInfoWindow = new google.maps.InfoWindow({
        content: 'Origin'
    });
    const destinationInfoWindow = new google.maps.InfoWindow({
        content: 'Destination'
    });

    originInfoWindow.open(originMap, originMarker);
    destinationInfoWindow.open(destinationMap, destinationMarker);
    originMap.addListener('click', function(event) {
        originMarker.setPosition(event.latLng);
        document.getElementById('ship_from_lat').value = event.latLng.lat();
        document.getElementById('ship_from_lng').value = event.latLng.lng();
    });
    destinationMap.addListener('click', function(event) {
        destinationMarker.setPosition(event.latLng);
        document.getElementById('ship_to_lat').value = event.latLng.lat();
        document.getElementById('ship_to_lng').value = event.latLng.lng();
    });


}

function loadGoogleMaps() {
    const script = document.createElement('script');
    script.src = `https://maps.googleapis.com/maps/api/js?key=AIzaSyA6mmmEz_JCmb6p-yD6RnDPtRt7o4SXjh8&callback=initMaps`;
    script.async = true;
    script.defer = true;
    document.head.appendChild(script);
}

document.addEventListener("DOMContentLoaded", () => {
    loadGoogleMaps();
});
