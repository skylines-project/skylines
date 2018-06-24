import { getOwner } from '@ember/application';
import { computed } from '@ember/object';

export default function computedComponent(baseNameProperty, prefix = '') {
  return computed(baseNameProperty, function() {
    let componentName = this.get(baseNameProperty);
    if (!componentName) {
      return;
    }

    let container = getOwner(this);
    let fullComponentName = `${prefix}${componentName}`;

    if (
      container.lookup(`component:${fullComponentName}`) ||
      container.lookup(`template:components/${fullComponentName}`)
    ) {
      return fullComponentName;
    }
  });
}
