import { debug } from '@ember/debug';
import Service from '@ember/service';

import { task } from 'ember-concurrency';

export default class CesiumLoaderService extends Service {
  loaderPromise = null;

  load() {
    let promise = this.loaderPromise;
    if (!promise) {
      promise = this.loadTask.perform();
      this.set('loaderPromise', promise);
    }

    return promise;
  }

  @(task(function* () {
    debug('Loading Cesium...');
    yield loadJS('/cesium/Cesium.js');
  }).drop())
  loadTask;
}

function loadJS(url) {
  return new Promise(resolve => {
    let script = document.createElement('script');
    script.src = url;
    script.onload = resolve;
    document.body.appendChild(script);
  });
}
