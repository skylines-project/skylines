import Component from '@ember/component';
import { action, computed } from '@ember/object';
import { htmlSafe } from '@ember/template';

export default class extends Component {
  tagName = '';

  selectable = false;

  @computed('row.color')
  get badgeStyle() {
    return htmlSafe(`background-color: ${this.row.color}`);
  }

  @action
  remove() {
    this.onRemove(this.get('row.id'));
  }

  @action
  handleClick() {
    if (this.selectable) {
      this.onSelect(this.get('row.id'));
    }
  }
}
