import Ember from 'ember';

export default Ember.Component.extend({
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
