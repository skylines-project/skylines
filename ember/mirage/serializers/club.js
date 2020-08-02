import BaseSerializer from './application';

export default BaseSerializer.extend({
  serialize(object) {
    let json = BaseSerializer.prototype.serialize.apply(this, arguments);

    if (object.owner) {
      json.owner = {
        id: object.owner.id,
        name: object.owner.name,
      };
    } else {
      json.owner = null;
    }

    return json;
  },
});
