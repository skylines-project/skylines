import Ember from 'ember';
import { conditional } from 'ember-awesome-macros';
import raw from 'ember-macro-helpers/raw';

export default Ember.Controller.extend({
  account: Ember.inject.service(),

  notificationsTarget: conditional('account.user', raw('notifications'), raw('timeline')),
});
