/* global BigScreen */

import Ember from 'ember';
import $ from 'jquery';

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
    BigScreen.toggle($(element)[0]);
  },
});
