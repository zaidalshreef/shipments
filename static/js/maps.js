function initMaps() {
    const origin = {
        lat: parseFloat('{{ ship_from_lat }}'),
        lng: parseFloat('{{ ship_from_lng }}')
    };
    const destination = {
        lat: parseFloat('{{ ship_to_lat }}'),
        lng: parseFloat('{{ ship_to_lng }}')
    };

    const mapOptions = {
        zoom: 7,
        center: origin
    };
    const originMap = new google.maps.Map(document.getElementById('originMap'), mapOptions);
    const destinationMap = new google.maps.Map(document.getElementById('destinationMap'), mapOptions);

    const originMarker = new google.maps.Marker({
        position: origin,
        map: originMap,
        title: 'Origin'
    });
    const destinationMarker = new google.maps.Marker({
        position: destination,
        map: destinationMap,
        title: 'Destination'
    });

    originMarker.addListener('click', () => {
        window.open(`https://www.google.com/maps/search/?api=1&query=${origin.lat},${origin.lng}`, '_blank');
    });

    destinationMarker.addListener('click', () => {
        window.open(`https://www.google.com/maps/search/?api=1&query=${destination.lat},${destination.lng}`, '_blank');
    });
}

