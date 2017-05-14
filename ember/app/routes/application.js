import Ember from 'ember';
import RSVP from 'rsvp';
import ApplicationRouteMixin from 'ember-simple-auth/mixins/application-route-mixin';

import _availableLocales from '../utils/locales';

const FALLBACK_LOCALE = 'en';

export default Ember.Route.extend(ApplicationRouteMixin, {
  account: Ember.inject.service(),
  ajax: Ember.inject.service(),
  cookies: Ember.inject.service(),
  intl: Ember.inject.service(),
  session: Ember.inject.service(),
  units: Ember.inject.service(),

  async beforeModel() {
    let locale = await this._determineLocale();
    await this.get('intl').loadAndSetLocale(locale);
  },

  setupController(controller) {
    this._super(...arguments);

    let settings = this.get('session.data.authenticated.settings');
    if (settings) {
      this.get('units').setProperties({
        altitudeUnitIndex: settings.altitudeUnit,
        distanceUnitIndex: settings.distanceUnit,
        liftUnitIndex: settings.liftUnit,
        speedUnitIndex: settings.speedUnit,
      });
    }

    controller.set('uploadController', this.controllerFor('flight-upload'));
  },

  activate() {
    this._super(...arguments);

    let user = this.get('account.user');
    if (user) {
      this.get('raven').callRaven('setUserContext', user);
    }
  },

  async _determineLocale() {
    let availableLocales = _availableLocales.map(it => it.code);
    Ember.debug(`Available locales: ${availableLocales}`);

    let cookieLocale = this.get('cookies').read('locale');
    Ember.debug(`Locale from "locale" cookie: ${cookieLocale}`);

    if (!Ember.isBlank(cookieLocale) && availableLocales.includes(cookieLocale)) {
      Ember.debug(`Using locale "${cookieLocale}" from cookie`);
      return RSVP.resolve(cookieLocale);
    }

    Ember.debug('Requesting locale resolution from server');
    try {
      let data = { available: availableLocales.join() };
      return (await this.get('ajax').request('/api/locale', { data })).locale || FALLBACK_LOCALE;
    } catch (error) {
      return FALLBACK_LOCALE;
    }
  },

  sessionAuthenticated() {
    const attemptedTransition = this.get('session.attemptedTransition');
    const inLoginRoute = this.controllerFor('application').get('inLoginRoute');

    if (attemptedTransition) {
      attemptedTransition.retry();
      this.set('session.attemptedTransition', null);
    } else if (inLoginRoute) {
      this.transitionTo('index');
    }
  },
});
