import { assert, debug } from '@ember/debug';
import { inject as service } from '@ember/service';

import IntlService from 'ember-intl/services/intl';
import { Promise } from 'rsvp';

export default IntlService.extend({
  ajax: service(),
  cookies: service(),

  async loadIntlPolyfill() {
    await loadJS(`/assets/intl/intl.min.js`);
  },

  async loadAndSetLocale(locale) {
    await this.loadLocale(locale);
    this.setLocale(locale);
  },

  async loadLocale(locale) {
    assert('locale is set', locale);

    if (this.exists('yes', locale)) {
      return;
    }

    let promises = [this._loadTranslation(locale)];

    if (window.Intl === window.IntlPolyfill) {
      promises.push(this._loadPolyfillData(locale));
    }

    await Promise.all(promises);
  },

  async _loadTranslation(locale) {
    assert('locale is set', locale);

    debug(`Loading translations for locale: ${locale}`);
    let translations = await this.ajax.request(`/translations/${locale}.json`);
    await this.addTranslations(locale, translations);
  },

  async _loadPolyfillData(locale) {
    assert('locale is set', locale);
    debug(`Loading polyfill data for locale: ${locale}`);
    await loadJS(`/assets/intl/locales/${locale}.js`);
  },

  setLocale(locale) {
    debug(`Setting locale to "${locale}"`);
    this._super(...arguments);
    this.cookies.write('locale', locale, { path: '/', expires: new Date('2099-12-31') });

    document.documentElement.lang = locale;
  },
});

function loadJS(url) {
  return new Promise(resolve => {
    debug('Loading Cesium...');

    let el = document.createElement('script');
    el.src = url;
    el.onload = resolve;
    document.body.appendChild(el);
  });
}
