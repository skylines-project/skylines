/* global BigScreen */

import Component from '@ember/component';

import $ from 'jquery';

export default Component.extend({
  classNames: ['FullscreenButton', 'ol-unselectable'],

  click() {
    this.toggle();
  },

  toggle() {
    let element = this.fullscreenElement;
    BigScreen.toggle($(element)[0]);
  },
});
