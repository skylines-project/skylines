import { computed } from '@ember/object';
import { isNone as _isNone } from '@ember/utils';

export default function isNone(key) {
  return computed(key, function() {
    return _isNone(this.get(key));
  });
}
