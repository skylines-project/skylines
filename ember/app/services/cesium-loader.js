import Ember from 'ember';

const CESIUM_BASE_URL = '/cesium/';

export default Ember.Service.extend({
  loaderPromise: null,

  init() {
    this._super(...arguments);
    window.cesiumLoader = this;
  },

  load() {
    let promise = this.get('loaderPromise');
    if (!promise) {
      promise = new Ember.RSVP.Promise(resolve => {
        let cesium = document.createElement('script');
        cesium.src = CESIUM_BASE_URL + 'Cesium.js';
        cesium.onload = resolve;
        document.body.appendChild(cesium);
      });

      this.set('loaderPromise', promise);
    }

    return promise;
  },
});
