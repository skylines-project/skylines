import Ember from 'ember';

export default Ember.Controller.extend({
  queryParams: ['page', 'column', 'order'],
  page: 1,
  column: 'date',
  order: 'desc',
});
