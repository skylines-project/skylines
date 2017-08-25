import Ember from 'ember';

export default Ember.Component.extend({
  classNames: ['CesiumSwitcher', 'ol-unselectable'],

  enabled: false,
  onEnable() {},
  onDisable() {},

  click() {
    this.toggle();
  },

  touchEnd() {
    this.toggle();
  },

  toggle() {
    if (this.get('enabled')) {
      this.get('onDisable')();
    } else {
      this.get('onEnable')();
    }
  },
});
