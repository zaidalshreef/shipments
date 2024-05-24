let originMap;
let originMarker;
let destinationMap;
let destinationMarker;

async function initMaps() {
    const origin = {
        lat: parseFloat(document.getElementById('ship_from_lat').value),
        lng: parseFloat(document.getElementById('ship_from_lng').value)
    };
    const destination = {
        lat: parseFloat(document.getElementById('ship_to_lat').value),
        lng: parseFloat(document.getElementById('ship_to_lng').value)
    };

     originMap = await new google.maps.Map(document.getElementById('originMap'), {
        center: origin,
        zoom: 12
    });

     destinationMap = await new google.maps.Map(document.getElementById('destinationMap'), {
        center: destination,
        zoom: 12
    });


    originMarker = await new google.maps.Marker({
        position: origin,
        map: originMap,
        draggable: false
    });

    destinationMarker = await new google.maps.Marker({
        position: destination,
        map: destinationMap,
        draggable: false
    });


}

function loadGoogleMaps() {
    const script = document.createElement('script');
    script.src = `https://maps.googleapis.com/maps/api/js?key=AIzaSyA6mmmEz_JCmb6p-yD6RnDPtRt7o4SXjh8&callback=initMaps`;
    script.async = true;
    script.defer = true;
    document.head.appendChild(script);
}

document.addEventListener("DOMContentLoaded", async () => {
    await loadGoogleMaps();
});
