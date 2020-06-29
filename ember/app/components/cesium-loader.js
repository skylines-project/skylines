import Component from '@ember/component';
import { inject as service } from '@ember/service';

export default Component.extend({
  cesiumLoader: service(),

  tagName: '',

  init() {
    this._super(...arguments);
    this.cesiumLoader.load();
  },
});
