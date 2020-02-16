import Route from '@ember/routing/route';

export default Route.extend({
  model(params) {
    let ids = params.groupflight_ids.split(',').map(it => parseInt(it, 10));
    return { ids };
  },
});
