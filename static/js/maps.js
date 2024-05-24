
let originMap;
let destinationMap;

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
    const originMap = new Map(document.getElementById('originMap'), mapOptions);
    const destinationMap = new Map(document.getElementById('destinationMap'), mapOptions);

    const originMarker = new AdvancedMarkerElement({
        position: origin,
        map: originMap,
        title: 'Origin',
        gmpClickable: true
    });

    const destinationMarker = new AdvancedMarkerElement({
        position: destination,
        map: destinationMap,
        title: 'Destination',
        gmpClickable: true
    });


    originMarker.addListener('click', ({ domEvent, latLng }) => {
       console.log('originMarker clicked');
        window.open(`https://www.google.com/maps/search/?api=1&query=${origin.lat},${origin.lng}`, '_blank');
    });

    destinationMarker.addListener('click', ({ domEvent, latLng }) => {
      console.log('destinationMarker clicked');
        window.open(`https://www.google.com/maps/search/?api=1&query=${destination.lat},${destination.lng}`, '_blank');
    });
}

initMaps();