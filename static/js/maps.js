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

    // Create an info window to share between markers.
    const infoWindow = new google.maps.InfoWindow();

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
        infoWindow.close();
        const contentString = `
            <div>
                <h3>Ship From Location</h3>
                <p><strong>Name:</strong> ${document.getElementById('ship_from_name').value}</p>
                <p><strong>Address:</strong> ${document.getElementById('ship_from_address').value}</p>
                <a href="https://www.google.com/maps/search/?api=1&query=${origin.lat},${origin.lng}" target="_blank">View on Google Maps</a>
            </div>`;
        infoWindow.setContent(contentString);
        infoWindow.open(originMarker.getMap(), originMarker);
    });

    // Add a click listener for the destination marker
    destinationMarker.addListener("click", () => {
        infoWindow.close();
        const contentString = `
            <div>
                <h3>Ship To Location</h3>
                <p><strong>Name:</strong> ${document.getElementById('ship_to_name').value}</p>
                <p><strong>Address:</strong> ${document.getElementById('ship_to_address').value}</p>
                <a href="https://www.google.com/maps/search/?api=1&query=${destination.lat},${destination.lng}" target="_blank">View on Google Maps</a>
            </div>`;
        infoWindow.setContent(contentString);
        infoWindow.open(destinationMarker.getMap(), destinationMarker);
    });
}

window.initMap = initMap;
