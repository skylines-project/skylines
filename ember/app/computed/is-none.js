import Ember from 'ember';

export default function isNone(key) {
  return Ember.computed(key, function() {
    return Ember.isNone(this.get(key));
  });
}
