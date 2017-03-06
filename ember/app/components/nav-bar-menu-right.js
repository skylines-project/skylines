import Ember from 'ember';
import { findBy } from 'ember-awesome-macros/array';
import raw from 'ember-macro-helpers/raw';

import availableLocales from '../utils/locales';

export default Ember.Component.extend({
  account: Ember.inject.service(),
  intl: Ember.inject.service(),
  session: Ember.inject.service(),

  tagName: 'ul',
  classNames: ['nav', 'navbar-nav', 'navbar-right'],

  availableLocales,
  currentLocale: findBy('availableLocales', raw('code'), 'intl.locale.firstObject'),

  actions: {
    setLocale(locale) {
      this.get('intl').loadAndSetLocale(locale);
    },
  },
});
