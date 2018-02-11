import Route from '@ember/routing/route';

export default Route.extend({
  queryParams: {
    year: { refreshModel: true },
  },

  model() {},
});
