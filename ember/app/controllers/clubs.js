import Controller from '@ember/controller';

export default Controller.extend({
  queryParams: ['year'],
  year: new Date().getFullYear().toString(),
});
