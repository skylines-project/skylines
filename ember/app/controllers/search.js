import Controller from '@ember/controller';
import { action } from '@ember/object';
import { oneWay, readOnly } from '@ember/object/computed';

export default class SearchController extends Controller {
  queryParams = ['text'];

  @readOnly('text') searchText;
  @oneWay('searchText') searchTextInput;
  @readOnly('model.results') results;

  @action
  search(text) {
    this.transitionToRoute({ queryParams: { text } });
  }
}
