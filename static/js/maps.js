function initMap() {
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
        center: origin,
    };
    const originMap = new google.maps.Map(document.getElementById('originMap'), mapOptions);
    const destinationMap = new google.maps.Map(document.getElementById('destinationMap'), mapOptions);

    const originMarker = new google.maps.marker.AdvancedMarkerElement({
        position: origin,
        map: originMap,
        title: 'Origin',
        gmpClickable: true,
    });

    const destinationMarker = new google.maps.marker.AdvancedMarkerElement({
        position: destination,
        map: destinationMap,
        title: 'Destination',
        gmpClickable: true,
    });


}
