import { debug } from '@ember/debug';
import Service from '@ember/service';

export default Service.extend({
  loaderPromise: null,

  load() {
    let promise = this.loaderPromise;
    if (!promise) {
      debug('Loading Cesium...');
      promise = loadJS('/cesium/Cesium.js');
      this.set('loaderPromise', promise);
    }

    return promise;
  },
});

function loadJS(url) {
  return new Promise(resolve => {
    let script = document.createElement('script');
    script.src = url;
    script.onload = resolve;
    document.body.appendChild(script);
  });
}
