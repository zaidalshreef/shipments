function initMap() {
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
        title: "Origin",
        label: "O",
        optimized: false,
    });

    const destinationMarker = new google.maps.Marker({
        position: destination,
        map: destinationMap,
        title: "Destination",
        label: "D",
        optimized: false,
    });

    // Add a click listener for the origin marker
    originMarker.addListener("click", () => {
        window.open = `https://www.google.com/maps/search/?api=1&query=${origin.lat},${origin.lng}`;

    });

    // Add a click listener for the destination marker
    destinationMarker.addListener("click", () => {
        window.open = `https://www.google.com/maps/search/?api=1&query=${destination.lat},${destination.lng}`;
    });
}

window.initMap = initMap;
