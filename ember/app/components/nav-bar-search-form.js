import { inject as service } from '@ember/service';
import Component from '@glimmer/component';

export default class NavBarSearchForm extends Component {
  @service('searchText') searchTextService;
}
