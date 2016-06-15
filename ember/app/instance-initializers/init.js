export function initialize(appInstance) {
  // boot up services
  appInstance.lookup('service:flight-phase');
  appInstance.lookup('service:fix-calc');
  appInstance.lookup('service:pinned-flights');
}

export default {
  name: 'init',
  initialize,
};
