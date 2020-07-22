import Component from '@glimmer/component';

import ol from 'openlayers';

export default class extends Component {
  layer = new ol.layer.Tile({});

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
