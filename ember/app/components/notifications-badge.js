import { computed } from '@ember/object';
import { inject as service } from '@ember/service';
import Component from '@ember/component';

export default Component.extend({
  notifications: service(),
  intl: service(),

  tagName: 'span',
  classNames: ['badge'],
  classNameBindings: ['notifications.hasUnread:badge-warning'],
  attributeBindings: ['title'],

  title: computed('intl.locale', function() {
    return this.get('intl').t('notifications');
  }),
});
