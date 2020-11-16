import { inject as service } from '@ember/service';
import Component from '@glimmer/component';

import { task } from 'ember-concurrency';

export default class NavBarUserMenu extends Component {
  @service account;
  @service session;

  @(task(function* () {
    yield this.session.invalidate();
  }).drop())
  logoutTask;
}
