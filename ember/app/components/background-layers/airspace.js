import Component from '@glimmer/component';

import TileLayer from 'ol/layer/Tile';
import XYZSource from 'ol/source/XYZ';

import config from '../../config/environment';

export default class extends Component {
  layer = new TileLayer({
    source: new XYZSource({
      url: `${config.SKYLINES_TILE_BASEURL || ''}/tiles/1.0.0/airspace+airports/EPSG3857/{z}/{x}/{y}.png`,
    }),
    zIndex: 10,
  });

  constructor() {
    super(...arguments);

    this.layer.setProperties({
      name: 'Airspace',
      id: 'Airspace',
      base_layer: false,
      display_in_layer_switcher: true,
    });

    this.args.map.addLayer(this.layer);
  }

  willDestroy() {
    this.args.map.removeLayer(this.layer);
  }
}
