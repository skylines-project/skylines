import Component from '@ember/component';

import ol from 'openlayers';

export default Component.extend({
  tagName: '',

  init() {
    this._super(...arguments);

    window.flightMap = this;

    let interactions = ol.interaction.defaults({
      altShiftDragRotate: false,
      pinchRotate: false,
    });

    let map = new ol.Map({
      view: new ol.View({
        center: ol.proj.transform([10, 50], 'EPSG:4326', 'EPSG:3857'),
        maxZoom: 17,
        zoom: 5,
      }),
      controls: ol.control.defaults().extend([new ol.control.ScaleLine()]),
      interactions,
      ol3Logo: false,
    });
    this.set('map', map);
  },
});
