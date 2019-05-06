import Component from '@ember/component';
import { computed } from '@ember/object';

export default Component.extend({
  tagName: '',

  column: null,
  defaultOrder: 'asc',

  cssClass: computed('class', function() {
    let _class = this['class'];
    if (_class) {
      return `${_class} sortable`;
    } else {
      return 'sortable';
    }
  }),
});
