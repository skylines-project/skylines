import BaseSerializer from './application';

export default BaseSerializer.extend({
  serialize(object, request) {
    let json = BaseSerializer.prototype.serialize.apply(this, arguments);

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
