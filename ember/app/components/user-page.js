import Ember from 'ember';

import slMapClickHandler from '../utils/map-click-handler';

export default Ember.Component.extend({
  didInsertElement() {
    let map = window.flightMap;

    map.fit();

    slMapClickHandler(map.get('map'));
  },
});
