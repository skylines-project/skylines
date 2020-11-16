import { getOwner } from '@ember/application';
import { computed, get } from '@ember/object';

export default function computedComponent(baseNameProperty, prefix = '') {
  return computed(baseNameProperty, function () {
    let componentName = get(this, baseNameProperty);
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
