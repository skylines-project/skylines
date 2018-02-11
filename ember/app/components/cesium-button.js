import Component from '@ember/component';

export default Component.extend({
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
