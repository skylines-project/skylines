import Component from '@ember/component';
import { inject as service } from '@ember/service';

import { BASE_LAYERS, OVERLAY_LAYERS } from '../services/map-settings';

export default Component.extend({
  tagName: '',

  mapSettings: service(),

  map: null,
  open: false,

  BASE_LAYERS,
  OVERLAY_LAYERS,

  actions: {
    open() {
      this.set('open', true);
    },
  },
});
