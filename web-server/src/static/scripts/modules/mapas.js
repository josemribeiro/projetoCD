var theMap;

var layerRoute;

var layerDistrict;
var layerCounty;

var latMyInitialPosition;
var lngMyInitialPosition;

var pinCenter;
var pinDistrict;
var pinCounty;

const defaultLatPosition = 38.7900248;
const defaultLngPosition = -9.2021936;

const iconSize = 50;

const defaultZoom = 10;

const osrKey = "5b3ce3597851110001cf624839defe1736044a39ac1399052ee090cd";

const popupOptions = {
  maxWidth: 400
}

const defaultMapOptions = {
  center: [ defaultLatPosition, defaultLngPosition ],
  zoom: defaultZoom
};

function upDateCoords(lat, lng) {
  let latPlaceHolder = document.getElementById( 'inputLat' );
  latMyInitialPosition = lat;
  latPlaceHolder.value = latMyInitialPosition;

  let lngPlaceHolder = document.getElementById( 'inputLng' );
  lngMyInitialPosition = lng;
  lngPlaceHolder.value = lngMyInitialPosition; 
}

function initVars() {
  layerRoute = null;

  layerDistrict = null;
  layerCounty = null;

  pinCenter = null;
  pinDistrict = null;
  pinCounty = null;

  if ( !navigator.geolocation ) {
    alert( "Browser does not suport geolocation. Using default values." );

    latMyInitialPosition = 39.69484;
    lngMyInitialPosition = -8.13031;
  }
  else {
    latMyInitialPosition = lngMyInitialPosition = null;

    navigator.geolocation.getCurrentPosition( 
      function(pos) {
        const coords = pos.coords;

        latMyInitialPosition = coords.latitude;
        lngMyInitialPosition = coords.longitude;

        const markerOptionsCenter = {
          title: "A minha posição.",
          draggable: true
        };

        upDateCoords( latMyInitialPosition, lngMyInitialPosition );

        pinCenter = new L.Marker( [ latMyInitialPosition, lngMyInitialPosition ] , markerOptionsCenter );
        pinCenter.addTo( theMap );
        pinCenter.on( 
          'move',
          (event) => {
            upDateCoords( event.target.getLatLng().lat, event.target.getLatLng().lng );
          }
        );
      } );
  }
}


// Função para mostrar o mapa de cada carro
// O mapId é diferente para cada carro
export function showMapa(latitude, longitude, mapId) {
  const specifiedMapOptions = {
    center: [latitude, longitude],
    zoom: 13 
  };

  const mapElement = document.getElementById(mapId);
  if (!mapElement) {
    console.error("Map container with ID ${mapId} not found.");
    return;
  }

  const showMap = new L.map(mapElement, specifiedMapOptions);


  const layer = new L.TileLayer('http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png');
  showMap.addLayer(layer);


  const markers = L.markerClusterGroup();
  const pinCarro = L.marker([latitude, longitude]);
  markers.addLayer(pinCarro);


  showMap.addLayer(markers);
}


export function initMapa() {
  initVars();
  // Creating a map object
  theMap = new L.map( document.getElementById( 'map' ), defaultMapOptions );

  // Creating a Layer object
  let layer = new L.TileLayer( 'http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png' );

  // Adding the layer to the map
  theMap.addLayer( layer );

  let markers = L.markerClusterGroup();
  
  theMap.addLayer( markers );
}


export function resetMap() {
  if ( layerDistrict!=null ) {
    theMap.removeLayer( layerDistrict );
  }

  if ( layerCounty!=null ) {
    theMap.removeLayer( layerCounty );
  }

  if ( pinDistrict!=null ) {
    theMap.removeLayer( pinDistrict );
  }

  if ( pinCounty!=null ) {
    theMap.removeLayer( pinCounty );
  }

  theMap.setZoom( defaultZoom );
  theMap.panTo( L.latLng( defaultLatPosition, defaultLngPosition ), { animate: true } );
}