import Route from '@ember/routing/route';

export default Route.extend({
    afterModel() {
      let ids = this.modelFor('groupflight').ids;
      let gf_id = this.modelFor('groupflight').groupflight.id
      this.transitionTo('flight', gf_id +':' + ids.join(',')); //Groupflights start url with <groupflight_id>:
    }
});

