let originMap;
let originMarker;
let destinationMap;
let destinationMarker;

function initMaps() {
    const origin = {
        lat: parseFloat(document.getElementById('ship_from_lat').value),
        lng: parseFloat(document.getElementById('ship_from_lng').value)
    };
    const destination = {
        lat: parseFloat(document.getElementById('ship_to_lat').value),
        lng: parseFloat(document.getElementById('ship_to_lng').value)
    };

     originMap = new google.maps.Map(document.getElementById('originMap'), {
        center: origin,
        zoom: 12
    });

     destinationMap = new google.maps.Map(document.getElementById('destinationMap'), {
        center: destination,
        zoom: 12
    });

    originMarker = new google.maps.Marker({
        position: origin,
        map: originMap,
        title: 'Ship From Location',
    });

     destinationMarker= new google.maps.Marker({
        position: destination,
        map: destinationMap,
        title: 'Ship To Location',
         url: 'https://maps.google.com/maps?q=loc:'+destination.lat+','+destination.lng+''
    });

    // Add a click listener for each marker, and set up the info window.
      google.maps.event.addListener(originMarker,'click',function() {
          console.log("Origin Marker Clicked");
  });
        // Add a click listener for each marker, and set up the info window.
        google.maps.event.addListener(destinationMarker,'click',function() {
        console.log("Destination Marker Clicked");
    });

}

function loadGoogleMaps() {
    const script = document.createElement('script');
    script.src = `https://maps.googleapis.com/maps/api/js?key=AIzaSyA6mmmEz_JCmb6p-yD6RnDPtRt7o4SXjh8&callback=initMaps`;
    script.async = true;
    script.defer = true;
    document.head.appendChild(script);
}

document.addEventListener("DOMContentLoaded", () => {
    loadGoogleMaps();
});
