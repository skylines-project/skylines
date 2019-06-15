import Component from '@ember/component';
import { computed } from '@ember/object';
import { inject as service } from '@ember/service';

import availableLocales from '../utils/locales';

export default Component.extend({
  account: service(),
  intl: service(),
  session: service(),

  tagName: '',

  availableLocales,
  currentLocale: computed('availableLocales.@each.code', 'intl.locale', function() {
    return this.availableLocales.findBy('code', this.intl.locale[0]);
  }),

  actions: {
    setLocale(locale) {
      this.intl.loadAndSetLocale(locale);
    },
  },
});
