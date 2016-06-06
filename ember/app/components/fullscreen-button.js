/* global BigScreen */

import Ember from 'ember';

export default Ember.Component.extend({
  classNames: ['FullscreenButton', 'ol-unselectable'],

  click() {
    this.toggle();
  },

  touchEnd() {
    this.toggle();
  },

  toggle() {
    let element = this.get('fullscreenElement');
    BigScreen.toggle(Ember.$(element)[0]);
  },
});
