import { computed } from '@ember/object';
import Component from '@ember/component';

export default Component.extend({
  tagName: '',

  column: null,
  defaultOrder: 'asc',

  cssClass: computed('class', function() {
    let _class = this.get('class');
    if (_class) {
      return `${_class} sortable`;
    } else {
      return 'sortable';
    }
  }),
});
