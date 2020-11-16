import Route from '@ember/routing/route';
import { inject as service } from '@ember/service';

export default class IndexRoute extends Route {
  @service ajax;

  model() {
    return this.ajax.request('/api/live');
  }
}
