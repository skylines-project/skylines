import Route from '@ember/routing/route';
import { inject as service } from '@ember/service';
import RSVP from 'rsvp';

export default Route.extend({
  ajax: service(),

  model(params) {
  console.log(ids);
    let ids = this.modelFor('groupflight').ids.split(',').map(it => parseInt(it, 10));
    return { ids };
  },

  afterModel(model, transition) {
    this.transitionTo('flight', this.model.ids);
  },

});
