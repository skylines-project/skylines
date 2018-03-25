import { isBlank } from '@ember/utils';
import { debug } from '@ember/debug';
import { inject as service } from '@ember/service';
import Route from '@ember/routing/route';
import RSVP from 'rsvp';
import ApplicationRouteMixin from 'ember-simple-auth/mixins/application-route-mixin';

import _availableLocales from '../utils/locales';

const FALLBACK_LOCALE = 'en';

export default Route.extend(ApplicationRouteMixin, {
  account: service(),
  ajax: service(),
  cookies: service(),
  intl: service(),
  raven: service(),
  session: service(),
  units: service(),

  async beforeModel() {
    let locale = await this._determineLocale();
    await this.get('intl').loadAndSetLocale(locale);
  },

  setupController() {
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
    debug(`Available locales: ${availableLocales}`);

    let cookieLocale = this.get('cookies').read('locale');
    debug(`Locale from "locale" cookie: ${cookieLocale}`);

    if (!isBlank(cookieLocale) && availableLocales.includes(cookieLocale)) {
      debug(`Using locale "${cookieLocale}" from cookie`);
      return RSVP.resolve(cookieLocale);
    }

    debug('Requesting locale resolution from server');
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
