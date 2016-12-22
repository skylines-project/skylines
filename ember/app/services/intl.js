import Ember from 'ember';
import IntlService from 'ember-intl/services/intl';

export default IntlService.extend({
  ajax: Ember.inject.service(),
  cookies: Ember.inject.service(),

  loadAndSetLocale(locale) {
    return this.loadLocale(locale).then(() => this.setLocale(locale));
  },

  loadLocale(locale) {
    if (this.exists('yes', locale)) {
      return Ember.RSVP.resolve();
    }

    return this.get('ajax').request(`/translations/${locale}.json`)
      .then(translations => this.addTranslations(locale, translations));
  },

  setLocale(locale) {
    Ember.debug(`Setting locale to "${locale}"`);
    this._super(...arguments);
    this.get('cookies').write('locale', locale, { path: '/', expires: new Date('2099-12-31') });
  },
});
