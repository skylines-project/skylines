/* globals $ */

import { inject as service } from '@ember/service';

import Component from '@glimmer/component';
import { tracked } from '@glimmer/tracking';
import ol from 'openlayers';

export default class MapClickHandler extends Component {
  @service ajax;

  @tracked coordinate;
  @tracked closestFlight;
  @tracked locationData;

  /**
   * The OpenLayers.Geometry object of the circle.
   * @type {Object}
   */
  circle = { geometry: null, animation: null };

  /**
   * Stores the state if the infobox.
   * @type {Boolean}
   */
  visible = false;

  infobox = null;

  constructor() {
    super(...arguments);

    this.args.map.on('click', event => this.trigger(event));
  }

  get overlayPosition() {
    return this.closestFlight ? this.closestFlight.closestPoint : this.coordinate;
  }

  // Public attributes and functions

  /**
   * Click handler which shows a info box at the click location.
   *
   * @this {ol.Map}
   * @param {Event} event
   * @return {(boolean|undefined)}
   */
  trigger(event) {
    // Hide infobox if it's currently visible
    if (this.visible) {
      event.map.removeOverlay(this.infobox);
      this.hideCircle(0);
      this.visible = false;
      this.infobox = null;
      return;
    }

    if (!this.infobox) {
      this.infobox = new ol.Overlay({
        element: $('<div id="MapInfoBox" class="InfoBox"></div>').get(0),
      });
    }

    let infobox = this.infobox;
    let infobox_element = $(infobox.getElement());

    this.coordinate = event.coordinate;
    this.closestFlight = this.findClosestFlightPoint(this.coordinate);
    if (this.closestFlight) {
      // flight info
      let flight_info = this.flightInfo();
      infobox_element.append(flight_info);

      // near flights link
      let get_near_flights = this.nearFlights();
      infobox_element.append(get_near_flights);
    }

    // location info
    let get_location_info = this.locationInfo();
    infobox_element.append(get_location_info);

    event.map.addOverlay(infobox);
    infobox.setPosition(this.overlayPosition);
    this.showCircle(this.overlayPosition);

    this.visible = true;

    // stop bubbeling
    return false;
  }

  findClosestFlightPoint(coordinate) {
    let { flights, map } = this.args;
    if (!flights || !map) {
      return;
    }

    let { source } = flights;
    let feature = source.getClosestFeatureToCoordinate(coordinate);
    if (!feature) {
      return;
    }

    let geometry = feature.getGeometry();
    let closestPoint = geometry.getClosestPoint(coordinate);

    let inputPixel = map.getPixelFromCoordinate(coordinate);
    let featurePixel = map.getPixelFromCoordinate(closestPoint);

    let dx = inputPixel[0] - featurePixel[0];
    let dy = inputPixel[1] - featurePixel[1];
    let squaredDistance = dx * dx + dy * dy;
    if (squaredDistance > 100) {
      return;
    }

    let flightId = feature.get('sfid');
    let flight = flights.findBy('id', flightId);
    if (!flight) {
      return;
    }

    return { flight, closestPoint };
  }

  /**
   * Returns the flight badge element
   * @param {slFlight} flight Flight object
   * @return {jQuery}
   */
  flightInfo() {
    let { flight } = this.closestFlight;
    return $(`<span class="info-item badge" style="background:${flight.get('color')}">
      ${flight.getWithDefault('registration', '')}
    </span>`);
  }

  nearFlights() {
    let get_near_flights = $(`<div class="info-item">
      <a class="near" href="#NearFlights">Load nearby flights</a>
    </div>`);

    get_near_flights.on('click touchend', e => {
      let { flight, closestPoint } = this.closestFlight;
      let [lon, lat] = ol.proj.transform(closestPoint, 'EPSG:3857', 'EPSG:4326');
      let time = closestPoint[3];

      this.args.map.removeOverlay(this.infobox);
      this.getNearFlights(lon, lat, time, flight);
      this.visible = false;
      this.infobox = null;
      e.preventDefault();
    });

    return get_near_flights;
  }

  locationInfo() {
    let get_location_info = $(`<div class="info-item">
      <a class="near" href="#LocationInfo">Get location info</a>
    </div>`);

    get_location_info.on('click touchend', event => {
      let loc = ol.proj.transform(this.overlayPosition, 'EPSG:3857', 'EPSG:4326');
      this.getLocationInfo(loc[0], loc[1]);
      event.preventDefault();
    });

    return get_location_info;
  }

  /**
   * Show a circle at the clicked position
   *
   * @param {Array<Number>} coordinate Coordinate
   */
  showCircle(coordinate) {
    let stroke_style = new ol.style.Stroke({
      color: '#f4bd33',
      width: 3,
    });

    let circle_style = new ol.style.Style({ stroke: stroke_style });

    let circle = this.circle;
    if (!circle.geometry) {
      circle.geometry = new ol.geom.Circle(coordinate, 1000);
    } else {
      circle.geometry.setCenterAndRadius(coordinate, 1000);
    }

    circle.animation = null;

    let map = this.args.map;
    map.on('postcompose', function (e) {
      let vector_context = e.vectorContext;

      if (circle.geometry) {
        if (circle.animation !== null) {
          let frame_state = e.frameState;
          if (!circle.animation.start) {
            circle.animation.start = frame_state.time;
          }

          if (circle.animation.duration <= 0 || frame_state.time > circle.animation.start + circle.animation.duration) {
            circle.geometry = null;
            return;
          }

          let delta_time = -(circle.animation.start - frame_state.time) % circle.animation.duration;
          stroke_style.setWidth(3 - delta_time / (circle.animation.duration / 3));
        }

        vector_context.setStyle(circle_style);
        vector_context.drawCircle(circle.geometry);
        map.render();
      }
    });
  }

  /**
   * Hides the search circle
   *
   * @param {Number} duration Fade duration in ms
   */
  hideCircle(duration) {
    this.circle.animation = { duration, start: null };
  }

  /**
   * Request near flights via ajax
   *
   * @param {Number} lon Longitude.
   * @param {Number} lat Latitude.
   * @param {Number} time Time.
   * @param {slFlight} flight Flight.
   */
  async getNearFlights(lon, lat, time, flight) {
    let flights = this.args.flights;
    let addFlight = this.args.addFlight;
    if (!flights || !addFlight) {
      return;
    }

    try {
      let data = await this.ajax.request(`/api/flights/${flight.get('id')}/near?lon=${lon}&lat=${lat}&time=${time}`);

      for (let i = 0; i < data['flights'].length; ++i) {
        let flight = data['flights'][i];

        // skip retrieved flight if already on map
        if (flights.findBy('id', flight['sfid'])) {
          continue;
        }

        addFlight(flight);
      }
    } finally {
      this.hideCircle(1000);
    }
  }

  /**
   * Request location informations via ajax
   *
   * @param {Number} lon Longitude.
   * @param {Number} lat Latitude.
   */
  async getLocationInfo(lon, lat) {
    try {
      this.locationData = await this.ajax.request(`/api/mapitems?lon=${lon}&lat=${lat}`);
    } catch (error) {
      this.locationData = null;
    }
    this.showLocationData();
  }

  /**
   * Show location data in infobox
   *
   * @param {Object} data Location data.
   */
  showLocationData() {
    // do nothing if infobox is closed already
    if (!this.visible) {
      return;
    }

    let data = this.locationData;

    let infobox = this.infobox;
    let map = this.args.map;

    let element = $(infobox.getElement());
    element.empty();
    let item = $('<div class="location info-item"></div>');
    let no_data = true;

    if (data) {
      let airspace_layer = map
        .getLayers()
        .getArray()
        .filter(layer => layer.get('name') === 'Airspace')[0];
      let mwp_layer = map
        .getLayers()
        .getArray()
        .filter(layer => layer.get('name') === 'Mountain Wave Project')[0];

      if (!$.isEmptyObject(data['airspaces']) && airspace_layer.getVisible()) {
        let p = $('<p></p>');
        p.append(formatAirspaceData(data['airspaces']));
        item.append(p);
        no_data = false;
      }

      if (!$.isEmptyObject(data['waves']) && mwp_layer.getVisible()) {
        let p = $('<p></p>');
        p.append(formatMountainWaveData(data['waves']));
        item.append(p);
        no_data = false;
      }
    }

    if (no_data) {
      item.html('No data retrieved for this location');

      element.delay(1500).fadeOut(1000, () => {
        map.removeOverlay(infobox);
        this.visible = false;
      });

      this.hideCircle(1000);
    }

    element.append(item);
  }
}

/**
 * Format Airspace data for infobox
 *
 * @param {Object} data Airspace data.
 * @return {jQuery} HTML table with the airspace data.
 */
function formatAirspaceData(data) {
  let table = $('<table></table>');

  table.append(
    $(`<thead>
      <tr>
        <th colspan="4">Airspaces</th>
      </tr>
      <tr>
        <th>Name</th>
        <th>Class</th>
        <th>Base</th>
        <th>Top</th>
      </tr>
    </thead>`),
  );

  let table_body = $('<tbody></tbody>');

  for (let i = 0; i < data.length; ++i) {
    table_body.append(
      $(`<tr>
        <td class="airspace_name">${data[i]['name']}</td>
        <td class="airspace_class">${data[i]['class']}</td>
        <td class="airspace_base">${data[i]['base']}</td>
        <td class="airspace_top">${data[i]['top']}</td>
      </tr>`),
    );
  }

  table.append(table_body);

  return table;
}

/**
 * Format Mountain Wave data in infobox
 *
 * @param {Object} data Wave data.
 * @return {jQuery} HTML table with the wave data.
 */
function formatMountainWaveData(data) {
  let table = $('<table></table>');

  table.append(
    $(`<thead>
      <tr>
        <th colspan="2">Mountain Waves</th>
      </tr>
      <tr>
        <th>Name</th>
        <th>Wind direction</th>
      </tr>
    </thead>`),
  );

  let table_body = $('<tbody></tbody>');

  for (let i = 0; i < data.length; ++i) {
    let wind_direction = data[i]['main_wind_direction'] || 'Unknown';

    table_body.append(
      $(`<tr>
        <td class="wave_name">${data[i]['name']}</td>
        <td class="wave_direction">${wind_direction}</td>
      </tr>`),
    );
  }

  table.append(table_body);

  return table;
}
