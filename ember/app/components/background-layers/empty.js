import Component from '@glimmer/component';

import TileLayer from 'ol/layer/Tile';

export default class extends Component {
  layer = new TileLayer({});

  constructor() {
    super(...arguments);

    this.layer.setProperties({
      name: 'Empty',
      id: 'Empty',
      base_layer: true,
      display_in_layer_switcher: true,
    });

    this.args.map.addLayer(this.layer);
  }

  willDestroy() {
    this.args.map.removeLayer(this.layer);
  }
}
