import { debug } from '@ember/debug';
import { bool } from '@ember/object/computed';
import Service from '@ember/service';

import { task } from 'ember-concurrency';

export default class CesiumLoaderService extends Service {
  @bool('loadTask.lastSuccessful') loaded;

  load() {
    return this.loadTask.perform();
  }

  @(task(function* () {
    if (!this.loaded) {
      debug('Loading Cesium...');
      yield loadJS('/cesium/Cesium.js');
    }
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
