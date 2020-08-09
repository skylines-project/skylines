import Component from '@glimmer/component';

import TileLayer from 'ol/layer/Tile';
import OsmSource from 'ol/source/OSM';

export default class extends Component {
  layer = new TileLayer({
    source: new OsmSource({
      crossOrigin: 'anonymous',
    }),
    zIndex: 1,
  });

  constructor() {
    super(...arguments);

    this.layer.setProperties({
      name: 'OpenStreetMap',
      id: 'OpenStreetMap',
      base_layer: true,
      display_in_layer_switcher: true,
    });

    this.args.map.addLayer(this.layer);
  }

  willDestroy() {
    this.args.map.removeLayer(this.layer);
  }
}
