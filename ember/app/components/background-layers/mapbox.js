import Component from '@glimmer/component';

import TileLayer from 'ol/layer/Tile';
import XYZSource from 'ol/source/XYZ';

export default class extends Component {
  layer = new TileLayer({
    source: new XYZSource({
      attributions:
        '<a href="https://www.mapbox.com/about/maps/"' +
        ' target="_blank" rel="noopener">' +
        '&copy; Mapbox &copy; OpenStreetMap</a> <a' +
        ' class="mapbox-improve-map"' +
        ' href="https://www.mapbox.com/map-feedback/"' +
        ' target="_blank" rel="noopener">Improve this map</a>',
      crossOrigin: 'anonymous',
      url: this.args.url,
    }),
    zIndex: 5,
  });

  constructor() {
    super(...arguments);

    this.layer.setProperties({
      name: 'Terrain',
      id: 'Terrain',
      base_layer: true,
      display_in_layer_switcher: true,
    });

    this.args.map.addLayer(this.layer);
  }

  willDestroy() {
    this.args.map.removeLayer(this.layer);
  }
}
