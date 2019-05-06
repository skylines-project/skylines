import { debug } from '@ember/debug';
import Route from '@ember/routing/route';
import { inject as service } from '@ember/service';
import { isBlank } from '@ember/utils';
import Ember from 'ember';

import ApplicationRouteMixin from 'ember-simple-auth/mixins/application-route-mixin';
import RSVP from 'rsvp';

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
    if (!window.Intl) {
      debug(`Loading Intl.js polyfill...`);
      await this.intl.loadIntlPolyfill();
    }
    await this.intl.loadAndSetLocale(locale);
  },

  setupController() {
    this._super(...arguments);

    let settings = this.get('session.data.authenticated.settings');
    if (settings) {
      this.units.setProperties({
        altitudeUnitIndex: settings.altitudeUnit,
        distanceUnitIndex: settings.distanceUnit,
        liftUnitIndex: settings.liftUnit,
        speedUnitIndex: settings.speedUnit,
      });
    }
  },

  activate() {
    this._super(...arguments);

    let userId = this.get('account.user.id');
    if (userId) {
      this.raven.callRaven('setUserContext', { id: userId });
    }
  },

  async _determineLocale() {
    let availableLocales = _availableLocales.map(it => it.code);
    debug(`Available locales: ${availableLocales}`);

    let cookieLocale = Ember.testing ? undefined : this.cookies.read('locale');
    debug(`Locale from "locale" cookie: ${cookieLocale}`);

    if (!isBlank(cookieLocale) && availableLocales.includes(cookieLocale)) {
      debug(`Using locale "${cookieLocale}" from cookie`);
      return RSVP.resolve(cookieLocale);
    }

    debug('Requesting locale resolution from server');
    try {
      let data = { available: availableLocales.join() };
      return (await this.ajax.request('/api/locale', { data })).locale || FALLBACK_LOCALE;
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
