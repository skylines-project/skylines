import makeFunctionalModifier from 'ember-functional-modifiers';

export default makeFunctionalModifier((element, [map]) => {
  if (map) {
    map.setTarget(element);
    return () => map.setTarget(null);
  }
});
