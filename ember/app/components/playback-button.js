import Component from '@ember/component';

export default Component.extend({
  classNames: ['PlayButton', 'ol-unselectable'],

  onToggle() {},

  click() {
    this.toggle();
  },

  toggle() {
    this.onToggle();
  },
});
