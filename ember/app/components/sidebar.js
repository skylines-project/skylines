import { action } from '@ember/object';
import Component from '@glimmer/component';
import { tracked } from '@glimmer/tracking';

export default class Sidebar extends Component {
  @tracked collapsed;
  @tracked visibleTab;

  constructor() {
    super(...arguments);
    this.selectedTab = this.args.defaultTab;
  }

  get selectedTab() {
    return this.collapsed ? null : this.visibleTab;
  }

  set selectedTab(id) {
    if (!id) {
      this.collapsed = true;
    } else {
      this.visibleTab = id;
      this.collapsed = false;
    }
  }

  @action onSelect(id) {
    this.selectedTab = id;
  }
}
