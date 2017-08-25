import BaseMapComponent from './base-map';
import slMapClickHandler from '../utils/map-click-handler';

export default BaseMapComponent.extend({
  flights: null,
  fixes: null,
  phaseHighlightCoords: null,
  hoverEnabled: true,

  onExtentChange() {},
  onTimeChange() {},
  onCesiumEnabledChange() {},

  didInsertElement() {
    this._super(...arguments);

    let map = this.get('map');
    map.on('moveend', this._handleMoveEnd, this);
    map.on('pointermove', this._handlePointerMove, this);

    slMapClickHandler(this.get('map'), this.get('flights'), this.get('addFlight'));
  },

  willDestroyElement() {
    this._super(...arguments);
    let map = this.get('map');
    map.un('moveend', this._handleMoveEnd, this);
    map.un('pointermove', this._handlePointerMove, this);
  },

  _handleMoveEnd(event) {
    this.get('onExtentChange')(event.frameState.extent);
  },

  _handlePointerMove(event) {
    if (event.dragging || !this.get('hoverEnabled')) { return; }

    let map = this.get('map');
    let source = this.get('flights.source');

    let coordinate = map.getEventCoordinate(event.originalEvent);
    let feature = source.getClosestFeatureToCoordinate(coordinate);

    if (feature !== null) {
      let geometry = feature.getGeometry();
      let closest_point = geometry.getClosestPoint(coordinate);

      let feature_pixel = map.getPixelFromCoordinate(closest_point);
      let mouse_pixel = map.getPixelFromCoordinate(coordinate);

      let squared_distance = Math.pow(mouse_pixel[0] - feature_pixel[0], 2) +
        Math.pow(mouse_pixel[1] - feature_pixel[1], 2);

      // Set the time when the mouse hovers the map
      let time = (squared_distance > 100) ? this.get('defaultTime') : closest_point[3];
      this.get('onTimeChange')(time);

      map.render();
    }
  },

  actions: {
    cesiumEnabled() {
      this.set('cesiumEnabled', true);
      this.get('onCesiumEnabledChange')(true);
    },
    cesiumDisabled() {
      this.set('cesiumEnabled', false);
      this.get('onCesiumEnabledChange')(false);
    },
  },
});
