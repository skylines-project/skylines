import Ember from 'ember';

import slMapClickHandler from '../utils/map-click-handler';

export default Ember.Component.extend({
  didInsertElement() {
    let map = window.flightMap;
    if (map) {
      map.fit();
      slMapClickHandler(map.get('map'));
    }
  },
});
