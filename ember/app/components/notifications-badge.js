import Ember from 'ember';

export default Ember.Component.extend({
  notifications: Ember.inject.service(),

  tagName: 'span',
  classNames: ['badge'],
  classNameBindings: ['notifications.hasUnread:badge-warning'],
});
