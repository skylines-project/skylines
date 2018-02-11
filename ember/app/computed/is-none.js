import { isNone as _isNone } from '@ember/utils';
import { computed } from '@ember/object';

export default function isNone(key) {
  return computed(key, function() {
    return _isNone(this.get(key));
  });
}
