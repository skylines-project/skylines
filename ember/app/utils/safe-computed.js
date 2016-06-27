import Ember from 'ember';

export default function safeComputed(func) {
  let args;

  if (arguments.length > 1) {
    args = [].slice.call(arguments);
    func = args.pop();
  }

  args.push(function() {
    let values = [];
    for (let i = 0; i < args.length - 1; i++) {
      let value = this.get(args[i]);

      // drop out if any `value` is undefined
      if (Ember.isNone(value)) {
        return;
      }

      values.push(value);
    }

    return func.apply(this, values);
  });

  return Ember.computed(...args);
}
