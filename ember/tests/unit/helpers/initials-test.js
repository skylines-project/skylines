import { expect } from 'chai';
import { describe, it } from 'mocha';

import { initials } from 'skylines/helpers/initials';

describe('Unit | Helper | initials', function() {
  it('works', function() {
    expect(initials(['John Doe'])).to.equal('JD');
    expect(initials(['John Adam Bart Charly Doe'])).to.equal('JABCD');
    expect(initials(['John Fitz. Kennedy'])).to.equal('JK');
    expect(initials(['John F. Kennedy'])).to.equal('JK');
    expect(initials(['John F Kennedy'])).to.equal('JK');
  });
});
