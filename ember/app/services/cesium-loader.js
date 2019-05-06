import { debug } from '@ember/debug';
import Service from '@ember/service';

import RSVP from 'rsvp';

const CESIUM_BASE_URL = '/cesium/';

export default Service.extend({
  loaderPromise: null,

  load() {
    let promise = this.loaderPromise;
    if (!promise) {
      promise = new RSVP.Promise(resolve => {
        debug('Loading Cesium...');

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
