import Ember from 'ember';
import RSVP from 'rsvp';

const CESIUM_BASE_URL = '/cesium/';

export default Ember.Service.extend({
  loaderPromise: null,

  load() {
    let promise = this.get('loaderPromise');
    if (!promise) {
      promise = new RSVP.Promise(resolve => {
        Ember.debug('Loading Cesium...');

        let cesium = document.createElement('script');
        cesium.src = `${CESIUM_BASE_URL}Cesium.js`;
        cesium.onload = resolve;
        document.body.appendChild(cesium);
      });

      this.set('loaderPromise', promise);
    }

    return promise;
  },
});
