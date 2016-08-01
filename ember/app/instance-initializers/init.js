import Ember from 'ember';

export function initialize(appInstance) {
  // boot up services
  appInstance.lookup('service:account');
  appInstance.lookup('service:pinned-flights');

  appInstance.lookup('service:intl')
    .setLocale([Ember.$('meta[name=skylines-locale]').attr('content'), 'en']);
}

export default {
  name: 'init',
  initialize,
};
