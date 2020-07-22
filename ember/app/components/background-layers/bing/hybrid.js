import Component from '@glimmer/component';

import ol from 'openlayers';

export default class extends Component {
  layer = new ol.layer.Tile({
    source: new ol.source.BingMaps({
      key: this.args.apiKey,
      imagerySet: 'AerialWithLabels',
    }),
    zIndex: 4,
  });

  constructor() {
    super(...arguments);

    this.layer.setProperties({
      name: 'Bing Satellite',
      id: 'BingSatellite',
      base_layer: true,
      display_in_layer_switcher: true,
    });

    this.args.map.addLayer(this.layer);
  }

  willDestroy() {
    this.args.map.removeLayer(this.layer);
  }
}
