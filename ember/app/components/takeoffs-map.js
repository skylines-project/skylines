import slMapClickHandler from '../utils/map-click-handler';
import BaseMapComponent from './base-map';

export default BaseMapComponent.extend({
  didInsertElement() {
    this._super(...arguments);
    this.fit();
    slMapClickHandler(this.map);
  },

  fit() {
    let map = this.map;

    let layer = map
      .getLayers()
      .getArray()
      .find(layer => layer.get('id') === 'TakeoffLocations');

    if (layer) {
      let source = layer.getSource();
      let view = map.getView();

      view.fit(source.getExtent());

      let zoom = view.getZoom();
      if (zoom > 10) {
        view.setZoom(10);
      }
    }
  },
});
