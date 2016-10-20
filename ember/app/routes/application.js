import Ember from 'ember';
import { isUnauthorizedError } from 'ember-ajax/errors';
import RSVP from 'rsvp';

import _availableLocales from '../utils/locales';

export default Ember.Route.extend({
  account: Ember.inject.service(),
  ajax: Ember.inject.service(),
  cookies: Ember.inject.service(),
  intl: Ember.inject.service(),
  units: Ember.inject.service(),

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
    return this.get('ajax').request('/locale', { data }).then(it => it.locale || 'en');
  },

  model() {
    return this.get('ajax').request('/settings/').catch(error => {
      if (isUnauthorizedError(error)) {
        return {};
      } else {
        throw error;
      }
    });
  },

  setupController(controller, model) {
    if (model.id) {
      this.get('account').setProperties({
        user: {
          id: model.id,
          name: model.name,
        },
        club: model.club,
      });

      this.get('units').setProperties({
        altitudeUnitIndex: model.altitudeUnit,
        distanceUnitIndex: model.distanceUnit,
        liftUnitIndex: model.liftUnit,
        speedUnitIndex: model.speedUnit,
      });
    }
  },

  activate() {
    this._super(...arguments);

    let user = this.get('account.user');
    if (user) {
      this.get('raven').callRaven('setUserContext', user);
    }
  },
});
