import Component from '@ember/component';

export default Component.extend({
  classNames: ['PlayButton', 'ol-unselectable'],

  onToggle() {},

  click() {
    this.toggle();
  },

  touchEnd() {
    this.toggle();
  },

  toggle() {
    this.get('onToggle')();
  },
});
