import Component from '@ember/component';
import { action, getWithDefault, observer } from '@ember/object';
import { once } from '@ember/runloop';

import Icon from 'ol/style/Icon';
import Style from 'ol/style/Style';

const STYLES = {
  glider: createStyle({
    src: '/images/glider_symbol.png',
  }),
  motorglider: createStyle({
    src: '/images/motorglider_symbol.png',
  }),
  paraglider: createStyle({
    src: '/images/paraglider_symbol.png',
  }),
  hangglider: createStyle({
    size: [40, 14],
    src: '/images/hangglider_symbol.png',
  }),
};

function createStyle({ src, size = [40, 24] }) {
  let icon = new Icon({
    anchor: [0.5, 0.5],
    anchorXUnits: 'fraction',
    anchorYUnits: 'fraction',
    size,
    src,
    rotation: 0,
    rotateWithView: true,
  });

  icon.load();

  return new Style({ image: icon });
}

export default Component.extend({
  tagName: '',

  map: null,
  fixes: null,

  fixesObserver: observer('fixes.@each.pointXY', function () {
    once(this.map, 'render');
  }),

  didInsertElement() {
    this._super(...arguments);
    this.map.on('postcompose', this.onPostCompose, this);
  },

  willDestroyElement() {
    this._super(...arguments);
    this.map.un('postcompose', this.onPostCompose, this);
  },

  @action
  onPostCompose(e) {
    this.renderIcons(e.vectorContext);
  },

  renderIcons(context) {
    this.fixes.forEach(fix => {
      let point = fix.get('pointXY');

      if (point) {
        let type = getWithDefault(fix, 'flight.model.type', 'glider');
        let style = STYLES[type] || STYLES['glider'];

        style.getImage().setRotation(fix.get('heading'));
        context.setStyle(style);
        context.drawGeometry(point);
      }
    });
  },
});
