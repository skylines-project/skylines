export function initialize(appInstance) {
  // boot up services
  appInstance.lookup('service:account');
  appInstance.lookup('service:pinned-flights');

  appInstance.lookup('service:intl')
    .setLocale([window.slLocale, 'en']);
}

export default {
  name: 'init',
  initialize,
};
