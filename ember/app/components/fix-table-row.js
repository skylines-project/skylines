import { action, computed } from '@ember/object';
import { htmlSafe } from '@ember/template';
import Component from '@glimmer/component';

export default class extends Component {
  @computed('args.row.color')
  get badgeStyle() {
    return htmlSafe(`background-color: ${this.args.row.color}`);
  }

  @action
  remove() {
    this.onRemove(this.args.row.id);
  }

  @action
  handleClick() {
    if (this.args.selectable) {
      this.args.onSelect(this.args.row.id);
    }
  }
}
