import Ember from 'ember';
import RSVP from 'rsvp';

import _availableLocales from '../utils/locales';

export default Ember.Route.extend({
  account: Ember.inject.service(),
  ajax: Ember.inject.service(),
  cookies: Ember.inject.service(),
  intl: Ember.inject.service(),

  beforeModel() {
    return this._determineLocale().then(locale => this.get('intl').setLocale(locale));
  },

  _determineLocale() {
    let availableLocales = _availableLocales.map(it => it.code);
    Ember.debug(`Available locales: ${availableLocales}`);

    let cookieLocale = this.get('cookies').read('locale');
    Ember.debug(`Locale from "locale" cookie: ${cookieLocale}`);

    if (!Ember.isBlank(cookieLocale) && availableLocales.includes(cookieLocale)) {
      Ember.debug(`Using locale "${cookieLocale}" from cookie`);
      return RSVP.resolve(cookieLocale);
    }

    Ember.debug('Requesting locale resolution from server');
    let data = { available: availableLocales.join() };
    return this.get('ajax').request('/locale', { data }).then(it => it.locale);
  },

  activate() {
    this._super(...arguments);

    let user = this.get('account.user');
    if (user) {
      this.get('raven').callRaven('setUserContext', user);
    }
  },
});
