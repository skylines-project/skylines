import Ember from 'ember';

export default function computedComponent(baseNameProperty, prefix = '') {
  return Ember.computed(baseNameProperty, function() {
    let componentName = this.get(baseNameProperty);
    if (!componentName) {
      return;
    }

    let container = Ember.getOwner(this);
    let fullComponentName = `${prefix}${componentName}`;

    if (container.lookup(`component:${fullComponentName}`) ||
      container.lookup(`template:components/${fullComponentName}`)) {
      return fullComponentName;
    }
  });
}
