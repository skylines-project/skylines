import Component from '@glimmer/component';

import TileLayer from 'ol/layer/Tile';
import XYZSource from 'ol/source/XYZ';

export default class extends Component {
  layer = new TileLayer({
    source: new XYZSource({
      attributions:
        'SRTM relief maps from <a target="_blank" rel="noopener" ' +
        'href="http://maps-for-free.com/">maps-for-free.com</a>',
      url: 'http://maps-for-free.com/layer/relief/z{z}/row{y}/{z}_{x}-{y}.jpg',
    }),
    zIndex: 2,
  });

  constructor() {
    super(...arguments);

    this.layer.setProperties({
      name: 'Shaded Relief',
      id: 'ShadedRelief',
      base_layer: true,
      display_in_layer_switcher: true,
    });

    this.args.map.addLayer(this.layer);
  }

  willDestroy() {
    this.args.map.removeLayer(this.layer);
  }
}
