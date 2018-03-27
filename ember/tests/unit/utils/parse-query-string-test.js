import { module, test } from 'qunit';

import parseQueryString from 'skylines/utils/parse-query-string';

module('Unit | Utility | parse query string', function() {
  test('returns empty object on empty input', function(assert) {
    let result = parseQueryString('');
    assert.deepEqual(result, {});
  });

  test('parses query strings', function(assert) {
    let result = parseQueryString('a=5&b=abc');
    assert.deepEqual(result, {
      a: '5',
      b: 'abc',
    });
  });

  test('parses query strings with leading question mark', function(assert) {
    let result = parseQueryString('?foo=42');
    assert.deepEqual(result, {
      foo: '42',
    });
  });
});
