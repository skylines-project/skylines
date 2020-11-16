import BaseMapComponent from './base-map';

export default class TakeoffsMap extends BaseMapComponent {
  didInsertElement() {
    super.didInsertElement(...arguments);
    this.fit();
  }

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
  }
}
