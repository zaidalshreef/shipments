
function initMap() {
    const origin = {
        lat: parseFloat(document.getElementById('ship_from_lat').value),
        lng: parseFloat(document.getElementById('ship_from_lng').value)
    };
    const destination = {
        lat: parseFloat(document.getElementById('ship_to_lat').value),
        lng: parseFloat(document.getElementById('ship_to_lng').value)
    };

    const originMap =  new google.maps.Map(document.getElementById('originMap'), {
        center: origin,
        zoom: 7
    });

    const destinationMap =  new google.maps.Map(document.getElementById('destinationMap'), {
        center: destination,
        zoom: 7
    });

    // Create an info window to share between markers.
    const infoWindow = new google.maps.InfoWindow();

    const originMarker =  new google.maps.Marker({
        position: origin,
        map: originMap,
        title: "Origin",
        label: "O",
        optimized: false,
    });

    const destinationMarker =  new google.maps.Marker({
        position: destination,
        map: destinationMap,
        title: "Destination",
        label: "D",
        optimized: false,
    });

    // Add a click listener for each marker, and set up the info window.
    originMarker.addListener("click", () => {
      infoWindow.close();
      infoWindow.setContent(originMarker.getTitle());
      infoWindow.open(originMarker.getMap(), originMarker);
    });
    // Add a click listener for each marker, and set up the info window.
    destinationMarker.addListener("click", () => {
        infoWindow.close();
        infoWindow.setContent(destinationMarker.getTitle());
        infoWindow.open(destinationMarker.getMap(), destinationMarker);
    });

}

window.initMap = initMap;
