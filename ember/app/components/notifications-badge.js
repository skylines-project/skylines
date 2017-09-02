import Ember from 'ember';

export default Ember.Component.extend({
  notifications: Ember.inject.service(),
  intl: Ember.inject.service(),

  tagName: 'span',
  classNames: ['badge'],
  classNameBindings: ['notifications.hasUnread:badge-warning'],
  attributeBindings: ['title'],

  title: Ember.computed('intl.locale', function() {
    return this.get('intl').t('notifications');
  }),
});
