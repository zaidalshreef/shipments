let originMap;
let originMarker;
let destinationMap;
let destinationMarker;

async function initMap() {
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
        zoom: 7
    });

     destinationMap = await new google.maps.Map(document.getElementById('destinationMap'), {
        center: destination,
        zoom: 7
    });

    // Create an info window to share between markers.
    const infoWindow = new google.maps.InfoWindow();

    originMarker = await new google.maps.Marker({
        position: origin,
        map: originMap,
        title: "Origin",
        label: "O",
        optimized: false,
        draggable: false
    });

    destinationMarker = await new google.maps.Marker({
        position: destination,
        map: destinationMap,
        title: "Destination",
        label: "D",
        optimized: false,
        draggable: false
    });

    // Add a click listener for each marker, and set up the info window.
    originMarker.addListener("click", () => {
      infoWindow.close();
      infoWindow.setContent(marker.getTitle());
      infoWindow.open(marker.getMap(), marker);
    });
    // Add a click listener for each marker, and set up the info window.
    destinationMarker.addListener("click", () => {
      infoWindow.close();
      infoWindow.setContent(marker.getTitle());
      infoWindow.open(marker.getMap(), marker);
    });

}

window.initMap = initMap;
