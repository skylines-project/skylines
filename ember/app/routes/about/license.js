import Route from '@ember/routing/route';
import { inject as service } from '@ember/service';

export default class LicenseRoute extends Route {
  @service ajax;

  model() {
    return this.ajax.request('/api/license');
  }
}
