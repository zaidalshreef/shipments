


function initMap() {
    const originMapElement = document.getElementById('originMap');
    const destinationMapElement = document.getElementById('destinationMap');

    const origin = {
        lat: parseFloat(originMapElement.dataset.lat),
        lng: parseFloat(originMapElement.dataset.lng),
        name: originMapElement.dataset.name,
        address: originMapElement.dataset.address
    };
    const destination = {
        lat: parseFloat(destinationMapElement.dataset.lat),
        lng: parseFloat(destinationMapElement.dataset.lng),
        name: destinationMapElement.dataset.name,
        address: destinationMapElement.dataset.address
    };

       const originlatAndlng = {lat: parseFloat(originMapElement.dataset.lat), lng: parseFloat(originMapElement.dataset.lng)};
       const destinationlatAndlng = {lat: parseFloat(destinationMapElement.dataset.lat), lng: parseFloat(destinationMapElement.dataset.lng)};

    const originMap = new google.maps.Map(originMapElement, {
        zoom: 14,
        center: originlatAndlng
    });
    const destinationMap = new google.maps.Map(destinationMapElement, {
        zoom: 14,
        center: destinationlatAndlng
    });

    const infoWindow = new google.maps.InfoWindow();


    const originMarker = new google.maps.Marker({
        position: origin,
        map: originMap,
        title: "Ship From Location",
        label: "O",
        optimized: false
    });

    const destinationMarker = new google.maps.Marker({
        position: destination,
        map: destinationMap,
        title: "Ship To Location",
        label: "D",
        optimized: false
    });

    originMarker.addListener("click", () => {
        infoWindow.close();
        const contentString = `
            <div style="font-family: Arial, sans-serif; font-size: 14px; text-align: center;">
                <p style="margin: 0;"><a href="https://www.google.com/maps/search/?api=1&query=${origin.lat},${origin.lng}" target="_blank" style="color: #2196F3;">View on Google Maps</a></p>
            </div>`;
        infoWindow.setContent(contentString);
        infoWindow.open(originMarker.getMap(), originMarker);
    });

    // Add a click listener for the destination marker
    destinationMarker.addListener("click", () => {
        infoWindow.close();
        const contentString = `
            <div style="font-family: Arial, sans-serif; font-size: 14px; text-align: center;">
                <p style="margin: 0;"><a href="https://www.google.com/maps/search/?api=1&query=${destination.lat},${destination.lng}" target="_blank" style="color: #2196F3;">View on Google Maps</a></p>
            </div>`;
        infoWindow.setContent(contentString);
        infoWindow.open(destinationMarker.getMap(), destinationMarker);
    });
}

window.initMap = initMap;
