import Ember from 'ember';

export default Ember.Component.extend({
  tagName: '',

  column: null,
  defaultOrder: 'asc',

  cssClass: Ember.computed('class', function() {
    let _class = this.get('class');
    if (_class) {
      return `${_class} sortable`;
    } else {
      return 'sortable';
    }
  }),
});
