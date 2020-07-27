import Component from '@ember/component';

import { defaults as controlDefaults } from 'ol/control';
import ScaleLine from 'ol/control/ScaleLine';
import { defaults as interactionDefaults } from 'ol/interaction';
import Map from 'ol/Map';
import { transform } from 'ol/proj';
import View from 'ol/View';

export default class BaseMap extends Component {
  tagName = '';

  constructor() {
    super(...arguments);

    window.flightMap = this;

    let controls = controlDefaults({ attributionOptions: { collapsible: true } }).extend([new ScaleLine()]);

    let interactions = interactionDefaults({
      altShiftDragRotate: false,
      pinchRotate: false,
    });

    let map = new Map({
      view: new View({
        center: transform([10, 50], 'EPSG:4326', 'EPSG:3857'),
        maxZoom: 17,
        zoom: 5,
      }),
      controls,
      interactions,
      ol3Logo: false,
    });
    this.set('map', map);
  }
}
