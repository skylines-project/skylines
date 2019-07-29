export function initialize(/* application */) {
  if (Intl.__disableRegExpRestore) {
    Intl.__disableRegExpRestore();
  }
}

export default {
  name: 'intl',
  initialize,
};
