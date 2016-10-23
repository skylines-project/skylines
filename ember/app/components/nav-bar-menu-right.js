import Ember from 'ember';
import availableLocales from '../utils/locales';

export default Ember.Component.extend({
  account: Ember.inject.service(),
  intl: Ember.inject.service(),
  session: Ember.inject.service(),

  tagName: 'ul',
  classNames: ['nav', 'navbar-nav', 'navbar-right'],

  availableLocales,
  currentLocale: Ember.computed('intl.locale', function() {
    let code = this.get('intl.locale.firstObject');
    return availableLocales.findBy('code', code);
  }),

  actions: {
    setLocale(locale) {
      this.get('intl').setLocale(locale);
    },
  },
});
