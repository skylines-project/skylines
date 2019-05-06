import Component from '@ember/component';
import { observer } from '@ember/object';
import { inject as service } from '@ember/service';

export default Component.extend({
  cesiumLoader: service(),

  tagName: '',

  enabled: false,
  loaded: false,

  enabledObserver: observer('enabled', function() {
    if (this.enabled && !this.loaded) {
      this.cesiumLoader.load().then(() => {
        this.set('loaded', true);
      });
    }
  }),
});
