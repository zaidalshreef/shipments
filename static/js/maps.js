function initMaps() {
    const origin = {
        lat: parseFloat(document.getElementById('ship_from_lat').value),
        lng: parseFloat(document.getElementById('ship_from_lng').value)
    };
    const destination = {
        lat: parseFloat(document.getElementById('ship_to_lat').value),
        lng: parseFloat(document.getElementById('ship_to_lng').value)
    };

    const mapOptions = {
        zoom: 7,
        center: origin
    };
    const originMap = new google.maps.Map(document.getElementById('originMap'), mapOptions);
    const destinationMap = new google.maps.Map(document.getElementById('destinationMap'), mapOptions);

    const originMarker = new google.maps.marker.AdvancedMarkerElement({
        position: origin,
        map: originMap,
        title: 'Origin',
        gmpClickable: true
    });

    const destinationMarker = new google.maps.marker.AdvancedMarkerElement({
        position: destination,
        map: destinationMap,
        title: 'Destination',
        gmpClickable: true
    });

    const infoWindow = new google.maps.InfoWindow();

    originMarker.addListener('click', ({ domEvent, latLng }) => {
        infoWindow.close();
        infoWindow.setContent(originMarker.title);
        infoWindow.open(originMap, originMarker);
        window.open(`https://www.google.com/maps/search/?api=1&query=${origin.lat},${origin.lng}`, '_blank');
    });

    destinationMarker.addListener('click', ({ domEvent, latLng }) => {
        infoWindow.close();
        infoWindow.setContent(destinationMarker.title);
        infoWindow.open(destinationMap, destinationMarker);
        window.open(`https://www.google.com/maps/search/?api=1&query=${destination.lat},${destination.lng}`, '_blank');
    });
}

window.initMaps = initMaps;