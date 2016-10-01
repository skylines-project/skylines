import Ember from 'ember';

export default Ember.Component.extend({
  classNames: ['PlayButton', 'ol-unselectable'],

  click() {
    this.toggle();
  },

  touchEnd() {
    this.toggle();
  },

  toggle() {
    this.getWithDefault('onToggle', Ember.K)();
  },
});
