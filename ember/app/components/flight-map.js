import BaseMapComponent from './base-map';

export default BaseMapComponent.extend({
  actions: {
    cesiumEnabled() {
      this.set('cesiumEnabled', true);
    },
    cesiumDisabled() {
      this.set('cesiumEnabled', false);
    },
  },
});
