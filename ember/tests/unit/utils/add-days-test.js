import { expect } from 'chai';
import { describe, it } from 'mocha';
import addDays from 'skylines/utils/add-days';

describe('addDays', function() {
  it('adds the specified days and returns an ISO formatted date', function() {
    expect(addDays('2016-06-24', 1)).to.equal('2016-06-25');
    expect(addDays('2016-06-24', 3)).to.equal('2016-06-27');
    expect(addDays('2016-06-24', 5)).to.equal('2016-06-29');
  });

  it('subtracts for negative days', function() {
    expect(addDays('2016-06-24', -1)).to.equal('2016-06-23');
    expect(addDays('2016-06-24', -3)).to.equal('2016-06-21');
    expect(addDays('2016-06-24', -5)).to.equal('2016-06-19');
  });

  it('handles wraparound', function() {
    expect(addDays('2016-06-30', 1)).to.equal('2016-07-01');
    expect(addDays('2016-07-01', -1)).to.equal('2016-06-30');
  });

  it('default returns same date', function() {
    expect(addDays('2016-06-24')).to.equal('2016-06-24');
  });
});
