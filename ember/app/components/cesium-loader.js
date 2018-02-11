import { observer } from '@ember/object';
import { inject as service } from '@ember/service';
import Component from '@ember/component';

export default Component.extend({
  cesiumLoader: service(),

  tagName: '',

  enabled: false,
  loaded: false,

  enabledObserver: observer('enabled', function() {
    if (this.get('enabled') && !this.get('loaded')) {
      this.get('cesiumLoader').load().then(() => {
        this.set('loaded', true);
      });
    }
  }),
});
