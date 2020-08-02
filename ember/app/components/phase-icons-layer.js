import Component from '@ember/component';
import { action } from '@ember/object';

import Feature from 'ol/Feature';
import Point from 'ol/geom/Point';
import VectorLayer from 'ol/layer/Vector';
import VectorSource from 'ol/source/Vector';
import Icon from 'ol/style/Icon';
import Style from 'ol/style/Style';

const START_ICON = new Icon({
  anchor: [0.5, 1],
  src: '/images/marker-green.png',
});

const END_ICON = new Icon({
  anchor: [0.5, 1],
  src: '/images/marker.png',
});

START_ICON.load();
END_ICON.load();

const START_STYLE = new Style({ image: START_ICON });
const END_STYLE = new Style({ image: END_ICON });

export default Component.extend({
  tagName: '',

  map: null,
  coordinates: null,

  init() {
    this._super(...arguments);

    this.layer = new VectorLayer({
      source: new VectorSource({
        useSpatialIndex: false,
      }),
      style(feature) {
        return feature.get('type') === 'end' ? END_STYLE : START_STYLE;
      },
      zIndex: 100,
    });

    this.map.addLayer(this.layer);

    this.updateSource();
  },

  willDestroy() {
    this._super(...arguments);
    this.map.removeLayer(this.layer);
  },

  @action
  updateSource() {
    let source = this.layer.getSource();

    source.clear();

    if (this.coordinates) {
      let startPoint = new Point(this.coordinates[0]);
      let endPoint = new Point(this.coordinates[this.coordinates.length - 1]);

      let startFeature = new Feature({ geometry: startPoint, type: 'start' });
      let endFeature = new Feature({ geometry: endPoint, type: 'end' });

      source.addFeature(startFeature);
      source.addFeature(endFeature);
    }
  },
});
