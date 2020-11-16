import Route from '@ember/routing/route';
import { inject as service } from '@ember/service';

export default class DetailsRoute extends Route {
  @service ajax;

  model({ user_ids }) {
    return this.ajax.request(`/api/live/${user_ids}`);
  }
}
