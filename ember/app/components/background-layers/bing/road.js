import Component from '@glimmer/component';

import TileLayer from 'ol/layer/Tile';
import BingSource from 'ol/source/BingMaps';

export default class extends Component {
  layer = new TileLayer({
    source: new BingSource({
      key: this.args.apiKey,
      imagerySet: 'Road',
    }),
    zIndex: 3,
  });

  constructor() {
    super(...arguments);

    this.layer.setProperties({
      name: 'Bing Road',
      id: 'BingRoad',
      base_layer: true,
      display_in_layer_switcher: true,
    });

    this.args.map.addLayer(this.layer);
  }

  willDestroy() {
    this.args.map.removeLayer(this.layer);
  }
}
