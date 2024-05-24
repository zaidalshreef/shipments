
let originMap;
let destinationMap;
let destinationMarker;
let originMarker;
async function initMaps() {
      const { Map } = await google.maps.importLibrary("maps");
        const { AdvancedMarkerElement } = await google.maps.importLibrary("marker");

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
     originMap = new Map(document.getElementById('originMap'), mapOptions);
     destinationMap = new Map(document.getElementById('destinationMap'), mapOptions);

     originMarker = new AdvancedMarkerElement({
        position: origin,
        map: originMap,
        title: 'Origin',
    });

     destinationMarker = new AdvancedMarkerElement({
        position: destination,
        map: destinationMap,
        title: 'Destination',
    });



}

initMaps();