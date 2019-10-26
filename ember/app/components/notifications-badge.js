import Component from '@ember/component';
import { computed } from '@ember/object';
import { inject as service } from '@ember/service';

export default Component.extend({
  notifications: service(),
  intl: service(),
  tagName: '',

  title: computed('intl.locale', function() {
    return this.intl.t('notifications');
  }),
});
