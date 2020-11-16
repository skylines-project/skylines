import Component from '@ember/component';
import { inject as service } from '@ember/service';

import safeComputed from '../../computed/safe-computed';

export default class Base extends Component {
  tagName = '';

  @service account;

  event = null;

  @safeComputed('account.user', 'event.actor', (accountUser, actor) => accountUser.id === actor.id)
  accountUserIsActor;
}
