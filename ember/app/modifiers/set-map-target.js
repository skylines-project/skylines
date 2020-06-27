import { modifier } from 'ember-modifier';

export default modifier((element, [map]) => {
  if (map) {
    map.setTarget(element);
    return () => map.setTarget(null);
  }
});
