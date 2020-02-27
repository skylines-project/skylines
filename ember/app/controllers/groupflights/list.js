import Controller from '@ember/controller';

export default Controller.extend({
  queryParams: ['page', 'column', 'order'],
  page: 1,
  column: 'date',
  order: 'desc',
});
