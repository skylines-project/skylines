import { action } from '@ember/object';
import Component from '@glimmer/component';

export default class SidebarTab extends Component {
  @action onClick(event) {
    event.preventDefault();
    event.stopPropagation();

    let { id, selectedTab } = this.args;
    this.args.onSelect(selectedTab === id ? null : id);
  }
}
