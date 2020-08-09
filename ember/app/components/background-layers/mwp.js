import Component from '@glimmer/component';

import TileLayer from 'ol/layer/Tile';
import XYZSource from 'ol/source/XYZ';

import config from '../../config/environment';

export default class extends Component {
  layer = new TileLayer({
    source: new XYZSource({
      attributions:
        'Mountain Wave Data &copy; ' +
        '<a href="http://www.mountain-wave-project.com/">' +
        'Mountain Wave Project' +
        '</a>.',
      crossOrigin: 'anonymous',
      url: `${config.SKYLINES_TILE_BASEURL || ''}/tiles/1.0.0/mwp/EPSG3857/{z}/{x}/{y}.png`,
    }),
    zIndex: 11,
  });

  constructor() {
    super(...arguments);

    this.layer.setProperties({
      name: 'Mountain Wave Project',
      id: 'MountainWaveProject',
      base_layer: false,
      display_in_layer_switcher: true,
    });

    this.args.map.addLayer(this.layer);
  }

  willDestroy() {
    this.args.map.removeLayer(this.layer);
  }
}
