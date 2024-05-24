function initMaps() {
    const origin = {
        lat: parseFloat(document.getElementById('ship_from_lat').value),
        lng: parseFloat(document.getElementById('ship_from_lng').value)
    };
    const destination = {
        lat: parseFloat(document.getElementById('ship_to_lat').value),
        lng: parseFloat(document.getElementById('ship_to_lng').value)
    };

    const originMap = new google.maps.Map(document.getElementById('originMap'), {
        center: origin,
        zoom: 12
    });

    const destinationMap = new google.maps.Map(document.getElementById('destinationMap'), {
        center: destination,
        zoom: 12
    });

    new google.maps.AdvancedMarkerElement({
        position: origin,
        map: originMap,
        title: 'Ship From Location',
        gmpClickable: true,

    });

    new google.maps.AdvancedMarkerElement({
        position: destination,
        map: destinationMap,
        title: 'Ship To Location',
        gmpClickable: true,

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
