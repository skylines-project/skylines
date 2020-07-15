import Component from '@ember/component';
import { action, computed } from '@ember/object';
import { inject as service } from '@ember/service';

import availableLocales from '../utils/locales';

export default class NavBarMenuRight extends Component {
  tagName = '';

  @service account;
  @service intl;
  @service session;

  availableLocales = availableLocales;

  @computed('availableLocales.@each.code', 'intl.locale')
  get currentLocale() {
    return this.availableLocales.findBy('code', this.intl.locale[0]);
  }

  @action
  setLocale(locale) {
    this.intl.loadAndSetLocale(locale);
  }
}
