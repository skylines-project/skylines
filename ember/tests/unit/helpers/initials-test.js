import { module, test } from 'qunit';

import { initials } from 'skylines/helpers/initials';

module('Unit | Helper | initials', function() {
  test('works', function(assert) {
    assert.equal(initials(['John Doe']), 'JD');
    assert.equal(initials(['John Adam Bart Charly Doe']), 'JABCD');
    assert.equal(initials(['John Fitz. Kennedy']), 'JK');
    assert.equal(initials(['John F. Kennedy']), 'JK');
    assert.equal(initials(['John F Kennedy']), 'JK');
  });
});
