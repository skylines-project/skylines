import { action } from '@ember/object';
import { inject as service } from '@ember/service';

import BaseMapComponent from './base-map';

export default class FlightMap extends BaseMapComponent {
  @service cesiumLoader;

  flights = null;
  fixes = null;
  phaseHighlightCoords = null;
  hoverEnabled = true;

  onExtentChange() {}
  onTimeChange() {}
  onCesiumEnabledChange() {}

  constructor() {
    super(...arguments);

    let map = this.map;
    map.on('moveend', this._handleMoveEnd);
    map.on('pointermove', this._handlePointerMove);
  }

  willDestroy() {
    super.willDestroy(...arguments);
    let map = this.map;
    map.un('moveend', this._handleMoveEnd);
    map.un('pointermove', this._handlePointerMove);
  }

  @action
  _handleMoveEnd(event) {
    this.onExtentChange(event.frameState.extent);
  }

  @action
  _handlePointerMove(event) {
    if (event.dragging || !this.hoverEnabled) {
      return;
    }

    let map = this.map;
    let source = this.get('flights.source');

    let coordinate = map.getEventCoordinate(event.originalEvent);
    let feature = source.getClosestFeatureToCoordinate(coordinate);

    if (feature !== null) {
      let geometry = feature.getGeometry();
      let closest_point = geometry.getClosestPoint(coordinate);

      let feature_pixel = map.getPixelFromCoordinate(closest_point);
      let mouse_pixel = map.getPixelFromCoordinate(coordinate);

      let squared_distance =
        Math.pow(mouse_pixel[0] - feature_pixel[0], 2) + Math.pow(mouse_pixel[1] - feature_pixel[1], 2);

      // Set the time when the mouse hovers the map
      let time = squared_distance > 100 ? this.defaultTime : closest_point[3];
      this.onTimeChange(time);

      map.render();
    }
  }

  @action enableCesium() {
    this.set('cesiumEnabled', true);
    this.onCesiumEnabledChange(true);
    this.cesiumLoader.load();
  }

  @action disableCesium() {
    this.set('cesiumEnabled', false);
    this.onCesiumEnabledChange(false);
  }
}
