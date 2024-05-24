
import dotenv from 'dotenv';

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
        zoom: 7
    });

    const destinationMap = new google.maps.Map(document.getElementById('destinationMap'), {
        center: destination,
        zoom: 7
    });

    const originMarker = new google.maps.Marker({
        position: origin,
        map: originMap,
        title: 'Ship From Location'
    });

    const destinationMarker = new google.maps.Marker({
        position: destination,
        map: destinationMap,
        title: 'Ship To Location'
    });
}

// Load the Google Maps script
function loadGoogleMaps(apiKey) {
    const script = document.createElement('script');
    script.src = `https://maps.googleapis.com/maps/api/js?key=${apiKey}&callback=initMaps`;
    script.async = true;
    script.defer = true;
    document.head.appendChild(script);
}

document.addEventListener("DOMContentLoaded", () => {
    const apiKey = document.getElementById('google-maps-api-key').value;
    loadGoogleMaps(apiKey);
});
