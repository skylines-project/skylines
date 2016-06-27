import BaseMapComponent from './base-map';

export default BaseMapComponent.extend({
  takeoffsLayer: null,

  fit() {
    let map = this.get('map');

    let layer = map.getLayers().getArray()
      .find(layer => (layer.get('id') === 'TakeoffLocations'));

    if (layer) {
      let source = layer.getSource();
      let view = map.getView();

      view.fit(source.getExtent(), map.getSize());

      let zoom = view.getZoom();
      if (zoom > 10) {
        view.setZoom(10);
      }
    }
  },
});
