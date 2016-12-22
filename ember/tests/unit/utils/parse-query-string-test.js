import { expect } from 'chai';
import { describe, it } from 'mocha';

import parseQueryString from 'skylines/utils/parse-query-string';

describe('Unit | Utility | parse query string', function() {
  it('returns empty object on empty input', function() {
    let result = parseQueryString('');
    expect(result).to.deep.equal({});
  });

  it('parses query strings', function() {
    let result = parseQueryString('a=5&b=abc');
    expect(result).to.deep.equal({
      a: '5',
      b: 'abc',
    });
  });

  it('parses query strings with leading question mark', function() {
    let result = parseQueryString('?foo=42');
    expect(result).to.deep.equal({
      foo: '42',
    });
  });
});
