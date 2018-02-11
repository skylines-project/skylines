import { inject as service } from '@ember/service';
import Component from '@ember/component';
import { findBy } from 'ember-awesome-macros/array';
import raw from 'ember-macro-helpers/raw';

import availableLocales from '../utils/locales';

export default Component.extend({
  account: service(),
  intl: service(),
  session: service(),

  tagName: '',

  availableLocales,
  currentLocale: findBy('availableLocales', raw('code'), 'intl.locale.firstObject'),

  actions: {
    setLocale(locale) {
      this.get('intl').loadAndSetLocale(locale);
    },
  },
});
