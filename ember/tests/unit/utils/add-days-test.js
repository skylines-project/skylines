import { module, test } from 'qunit';

import addDays from 'skylines/utils/add-days';

module('addDays', function() {
  test('adds the specified days and returns an ISO formatted date', function(assert) {
    assert.equal(addDays('2016-06-24', 1), '2016-06-25');
    assert.equal(addDays('2016-06-24', 3), '2016-06-27');
    assert.equal(addDays('2016-06-24', 5), '2016-06-29');
  });

  test('subtracts for negative days', function(assert) {
    assert.equal(addDays('2016-06-24', -1), '2016-06-23');
    assert.equal(addDays('2016-06-24', -3), '2016-06-21');
    assert.equal(addDays('2016-06-24', -5), '2016-06-19');
  });

  test('handles wraparound', function(assert) {
    assert.equal(addDays('2016-06-30', 1), '2016-07-01');
    assert.equal(addDays('2016-07-01', -1), '2016-06-30');
  });

  test('default returns same date', function(assert) {
    assert.equal(addDays('2016-06-24'), '2016-06-24');
  });
});
