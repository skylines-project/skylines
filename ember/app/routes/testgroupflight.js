import Route from '@ember/routing/route';

export default Route.extend({
  //model includes groupflight, flights, and paths
  model({ groupflight_id }) {
    return this.ajax.request(`/api/testgroupflight/${groupflight_id}`);
  },
});

