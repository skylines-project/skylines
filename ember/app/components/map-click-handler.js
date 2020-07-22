import { action } from '@ember/object';
import { inject as service } from '@ember/service';
import Component from '@glimmer/component';
import { tracked } from '@glimmer/tracking';

import { task } from 'ember-concurrency';
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

  constructor() {
    super(...arguments);

    this.args.map.on('click', event => this.trigger(event));
  }

  get overlayPosition() {
    return this.closestFlight ? this.closestFlight.closestPoint : this.coordinate;
  }

  @action addOverlay(element) {
    this.overlay = new ol.Overlay({ element, position: this.overlayPosition });
    this.args.map.addOverlay(this.overlay);
  }

  @action removeOverlay() {
    this.args.map.removeOverlay(this.overlay);
    this.overlay = null;
  }

  /**
   * Click handler which shows a info box at the click location.
   *
   * @this {ol.Map}
   * @param {Event} event
   * @return {(boolean|undefined)}
   */
  trigger(event) {
    // Hide infobox if it's currently visible
    if (this.coordinate) {
      this.hideCircle(0);
      this.coordinate = null;
      this.closestFlight = null;
      this.locationData = null;
      return;
    }

    this.coordinate = event.coordinate;
    this.closestFlight = this.findClosestFlightPoint(this.coordinate);
    this.locationData = null;

    this.showCircle(this.overlayPosition);

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

  @(task(function* () {
    let { flight, closestPoint } = this.closestFlight;
    let [lon, lat] = ol.proj.transform(closestPoint, 'EPSG:3857', 'EPSG:4326');
    let time = closestPoint[3];

    let flights = this.args.flights;
    let addFlight = this.args.addFlight;
    if (!flights || !addFlight) {
      return;
    }

    try {
      let data = yield this.ajax.request(`/api/flights/${flight.get('id')}/near?lon=${lon}&lat=${lat}&time=${time}`);

      for (let i = 0; i < data['flights'].length; ++i) {
        let flight = data['flights'][i];

        // skip retrieved flight if already on map
        if (flights.findBy('id', flight['sfid'])) {
          continue;
        }

        addFlight(flight);
      }
    } finally {
      this.coordinate = null;
      this.hideCircle(1000);
    }
  }).restartable())
  loadNearbyFlightsTask;

  @(task(function* () {
    let [lon, lat] = ol.proj.transform(this.overlayPosition, 'EPSG:3857', 'EPSG:4326');
    try {
      this.locationData = yield this.ajax.request(`/api/mapitems?lon=${lon}&lat=${lat}`);
    } catch (error) {
      this.locationData = null;
    }
  }).restartable())
  loadLocationInfoTask;
}
