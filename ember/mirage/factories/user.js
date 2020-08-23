import { Factory } from 'ember-cli-mirage';

export default Factory.extend({
  admin: false,
  altitudeUnit: 0,
  distanceUnit: 1,
  email: 'johnny.dee@gmail.com',
  firstName: 'John',
  followers: 107,
  following: 128,
  lastName: 'Doe',
  liftUnit: 0,
  name() {
    return `${this.firstName} ${this.lastName}`;
  },
  recoveryKey: null,
  speedUnit: 1,
  trackingCallsign: 'JD',
  trackingDelay: 0,
  trackingKey: 'ABCDEF42',
});
