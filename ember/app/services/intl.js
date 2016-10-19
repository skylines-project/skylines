import Ember from 'ember';
import IntlService from 'ember-intl/services/intl';

export default IntlService.extend({
  cookies: Ember.inject.service(),

  setLocale(locale) {
    Ember.debug(`Setting locale to "${locale}"`);
    this._super(...arguments);
    this.get('cookies').write('locale', locale, { path: '/', expires: new Date('2099-12-31') });
  },
});
