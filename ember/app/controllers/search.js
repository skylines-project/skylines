import { readOnly, oneWay } from '@ember/object/computed';
import Controller from '@ember/controller';

export default Controller.extend({
  queryParams: ['text'],

  searchText: readOnly('text'),
  searchTextInput: oneWay('searchText'),

  results: readOnly('model.results'),

  actions: {
    search(text) {
      this.transitionToRoute({ queryParams: { text } });
    },
  },
});
