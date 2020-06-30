import { setupTest } from 'ember-qunit';
import { module, test } from 'qunit';

module('Service | units', function (hooks) {
  setupTest(hooks);

  test('setting unit index changes the unit', function (assert) {
    let units = this.owner.lookup('service:units');
    assert.equal(units.distanceUnit, 'km');
    assert.equal(units.speedUnit, 'km/h');
    assert.equal(units.liftUnit, 'm/s');
    assert.equal(units.altitudeUnit, 'm');

    units.distanceUnitIndex = 2;
    units.speedUnitIndex = 3;
    units.liftUnitIndex = 2;
    units.altitudeUnitIndex = 1;

    assert.equal(units.distanceUnit, 'NM');
    assert.equal(units.speedUnit, 'mph');
    assert.equal(units.liftUnit, 'ft/min');
    assert.equal(units.altitudeUnit, 'ft');
  });

  test('setting unit changes the unit index', function (assert) {
    let units = this.owner.lookup('service:units');
    assert.equal(units.distanceUnitIndex, 1);
    assert.equal(units.speedUnitIndex, 1);
    assert.equal(units.liftUnitIndex, 0);
    assert.equal(units.altitudeUnitIndex, 0);

    units.distanceUnit = 'NM';
    units.speedUnit = 'mph';
    units.liftUnit = 'ft/min';
    units.altitudeUnit = 'ft';

    assert.equal(units.distanceUnitIndex, 2);
    assert.equal(units.speedUnitIndex, 3);
    assert.equal(units.liftUnitIndex, 2);
    assert.equal(units.altitudeUnitIndex, 1);
  });

  test('formatDistance()', function (assert) {
    let units = this.owner.lookup('service:units');
    assert.equal(units.formatDistance(1234567), '1,235 km');

    units.distanceUnitIndex = 0;
    assert.equal(units.formatDistance(1234567), '1,234,567 m');

    units.distanceUnitIndex = 2;
    assert.equal(units.formatDistance(1234567), '667 NM');
  });

  test('formatSpeed()', function (assert) {
    let units = this.owner.lookup('service:units');
    assert.equal(units.formatSpeed(123), '442.8 km/h');

    units.speedUnitIndex = 0;
    assert.equal(units.formatSpeed(123), '123.0 m/s');

    units.speedUnitIndex = 2;
    assert.equal(units.formatSpeed(123), '239.1 kt');
  });

  test('formatLift()', function (assert) {
    let units = this.owner.lookup('service:units');
    assert.equal(units.formatLift(4.2), '4.2 m/s');

    units.liftUnitIndex = 1;
    assert.equal(units.formatLift(4.2), '8.2 kt');
  });

  test('formatAltitude()', function (assert) {
    let units = this.owner.lookup('service:units');
    assert.equal(units.formatAltitude(1234), '1,234 m');

    units.altitudeUnitIndex = 1;
    assert.equal(units.formatAltitude(1234), '4,049 ft');
  });

  test('formatted values depend on the locale', function (assert) {
    let intl = this.owner.lookup('service:intl');

    intl.setLocale('en');

    let units = this.owner.lookup('service:units');
    assert.equal(units.formatAltitude(1234), '1,234 m');

    intl.setLocale('de');
    assert.equal(units.formatAltitude(1234), '1.234 m');
  });
});
