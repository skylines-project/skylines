import BaseSerializer from './application';

export default BaseSerializer.extend({
  serialize(object, request) {
    let json = BaseSerializer.prototype.serialize.apply(this, arguments);

    if (object.club) {
      json.club = {
        id: Number(object.club.id),
        name: object.club.name,
      };
    } else {
      json.club = null;
    }

    if (request.url.startsWith('/api/users/')) {
      delete json.altitudeUnit;
      delete json.distanceUnit;
      delete json.email;
      delete json.liftUnit;
      delete json.speedUnit;
      delete json.trackingKey;
    }

    return json;
  },
});
