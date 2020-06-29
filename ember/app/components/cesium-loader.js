import Component from '@ember/component';
import { observer } from '@ember/object';
import { inject as service } from '@ember/service';

export default Component.extend({
  cesiumLoader: service(),

  tagName: '',

  enabled: false,

  enabledObserver: observer('enabled', function () {
    if (this.enabled) {
      this.cesiumLoader.load();
    }
  }),
});
