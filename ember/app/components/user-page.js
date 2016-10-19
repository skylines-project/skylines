import Ember from 'ember';

export default Ember.Component.extend({
  didInsertElement() {
    let map = window.flightMap;
    if (map) {
      map.fit();
    }
  },
});
