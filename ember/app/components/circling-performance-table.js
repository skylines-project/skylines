import Ember from 'ember';

export default Ember.Component.extend({
  left: computedFindBy('perf', 'circlingDirection', 'left'),
  right: computedFindBy('perf', 'circlingDirection', 'right'),
  mixed: computedFindBy('perf', 'circlingDirection', 'mixed'),
  total: computedFindBy('perf', 'circlingDirection', 'total'),
});

function computedFindBy(arrayKey, key, value) {
  return Ember.computed(`${arrayKey}.${key}`, function() {
    return this.get(arrayKey).findBy(key, value);
  });
}
