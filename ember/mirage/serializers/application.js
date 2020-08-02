import { Serializer } from 'ember-cli-mirage';

export default Serializer.extend({
  embed: true,
  root: false,

  serialize() {
    let json = Serializer.prototype.serialize.apply(this, arguments);

    if ('id' in json) {
      json.id = Number(json.id);
    }

    return json;
  },
});
