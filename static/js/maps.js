

document.addEventListener("DOMContentLoaded", () => {
    loadGoogleMaps();
});

function loadGoogleMaps() {
    const script = document.createElement('script');
    script.src = `https://maps.googleapis.com/maps/api/js?key=${document.getElementById('google-maps-api-key').value}&callback=initMaps`;
    script.async = true;
    script.defer = true;
    document.head.appendChild(script);
}
