import { inject as service } from '@ember/service';
import Controller from '@ember/controller';
import { conditional } from 'ember-awesome-macros';
import raw from 'ember-macro-helpers/raw';

export default Controller.extend({
  account: service(),

  notificationsTarget: conditional('account.user', raw('notifications'), raw('timeline')),
});
