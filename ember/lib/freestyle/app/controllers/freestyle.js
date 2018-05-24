import FreestyleController from 'ember-freestyle/controllers/freestyle';

export default FreestyleController.extend({
  init() {
    this._super(...arguments);
    this.set('components', findAllUsageComponents());
  },
});

export function findAllUsageComponents() {
  let components = findUsageComponents();
  let templates = findUsageComponentTemplates();
  return [...components, ...templates].uniq().sort();
}

function findUsageComponents() {
  let pathPrefix = 'skylines/components/usage/';

  return Object.keys(require.entries)
    .filter(path => path.indexOf(pathPrefix) === 0)
    .map(path => path.slice(pathPrefix.length))
    .sort();
}

function findUsageComponentTemplates() {
  let pathPrefix = 'skylines/templates/components/usage/';

  return Object.keys(require.entries)
    .filter(path => path.indexOf(pathPrefix) === 0)
    .map(path => path.slice(pathPrefix.length))
    .sort();
}
