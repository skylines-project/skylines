import Component from '@ember/component';

export default Component.extend({
  classNames: ['CesiumSwitcher', 'ol-unselectable'],

  enabled: false,
  onEnable() {},
  onDisable() {},

  click() {
    this.toggle();
  },

  toggle() {
    if (this.enabled) {
      this.onDisable();
    } else {
      this.onEnable();
    }
  },
});
