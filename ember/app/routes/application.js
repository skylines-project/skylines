import { debug } from '@ember/debug';
import { action } from '@ember/object';
import Route from '@ember/routing/route';
import { inject as service } from '@ember/service';
import { isBlank } from '@ember/utils';
import Ember from 'ember';
import RSVP from 'rsvp';

import * as Sentry from '@sentry/browser';

import _availableLocales from '../utils/locales';

const FALLBACK_LOCALE = 'en';

export default class ApplicationRoute extends Route {
  @service account;
  @service ajax;
  @service cookies;
  @service intl;
  @service progress;
  @service session;
  @service units;

  async beforeModel() {
    let locale = await this._determineLocale();
    await this.intl.loadAndSetLocale(locale);
  }

  afterModel() {
    super.afterModel(...arguments);

    // remove loading spinner from the page (see `index.html`)
    let spinnner = document.querySelector('#initial-load-spinner');
    if (spinnner) {
      spinnner.classList.add('fade');
      setTimeout(() => spinnner.remove(), 1500);
    }
  }

  setupController() {
    super.setupController(...arguments);

    let settings = this.account.sessionData;
    if (settings) {
      this.units.altitudeUnitIndex = settings.altitudeUnit;
      this.units.distanceUnitIndex = settings.distanceUnit;
      this.units.liftUnitIndex = settings.liftUnit;
      this.units.speedUnitIndex = settings.speedUnit;
    }
  }

  activate() {
    super.activate(...arguments);

    let userId = this.get('account.user.id');
    if (userId) {
      Sentry.configureScope(scope => scope.setUser({ id: userId }));
    }
  }

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
  }

  @action
  loading(transition) {
    this.progress.handle(transition);
    return true;
  }
}
