import Component from '@ember/component';
import { action } from '@ember/object';

export default Component.extend({
  tagName: '',
  enabled: false,
  onEnable() {},
  onDisable() {},

  toggle: action(function() {
    if (this.enabled) {
      this.onDisable();
    } else {
      this.onEnable();
    }
  }),
});
