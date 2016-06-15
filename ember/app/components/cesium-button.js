import Ember from 'ember';

export default Ember.Component.extend({
  classNames: ['CesiumSwitcher', 'ol-unselectable'],

  enabled: false,

  click() {
    this.toggle();
  },

  touchEnd() {
    this.toggle();
  },

  toggle() {
    if (this.get('enabled')) {
      this.getWithDefault('onDisable', Ember.K)();
    } else {
      this.getWithDefault('onEnable', Ember.K)();
    }
  },
});
