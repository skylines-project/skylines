/* global BigScreen */

import Component from '@ember/component';
import { action } from '@ember/object';

import $ from 'jquery';

export default Component.extend({
  tagName: '',

  toggle: action(function() {
    let element = this.fullscreenElement;
    BigScreen.toggle($(element)[0]);
  }),
});
