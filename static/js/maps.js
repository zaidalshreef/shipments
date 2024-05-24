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
        title: 'Origin'
    });

    const destinationMarker = new google.maps.marker.AdvancedMarkerElement({
        position: destination,
        map: destinationMap,
        title: 'Destination'
    });

    originMarker.addListener('click', () => {
        window.open(`https://www.google.com/maps/search/?api=1&query=${origin.lat},${origin.lng}`, '_blank');
    });

    destinationMarker.addListener('click', () => {
        window.open(`https://www.google.com/maps/search/?api=1&query=${destination.lat},${destination.lng}`, '_blank');
    });
}

document.addEventListener("DOMContentLoaded", () => {
    loadGoogleMaps();
});

function loadGoogleMaps() {
    const script = document.createElement('script');
    script.src = `https://maps.googleapis.com/maps/api/js?key=${document.getElementById('google-maps-api-key').value}&callback=initMaps`;
    script.async = true;
    script.defer = true;
    document.head.appendChild(script);
}
