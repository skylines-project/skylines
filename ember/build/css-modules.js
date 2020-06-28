// roughly adapted from `base62`
function encodeNumber(int) {
  const charset = 'ScqZRQeBEdItMPlXCkJsFgDVLTzaHOmpxwNvoniAYhfKGrbyUjWu';

  int += charset.length;

  let res = '';
  while (int > 0) {
    res = charset[int % charset.length] + res;
    int = Math.floor(int / charset.length);
  }
  return res;
}

// this generates short, unique CSS class names for the CSS modules
// that ember-css-modules builds. in dev mode it includes the original
// class name, in prod mode it will only the short prefix.
let scopedNames = new Map();
function generateName(className, modulePath, { isProduction }) {
  let key = `${modulePath}->${className}`;
  if (!scopedNames.has(key)) {
    let scopedName = encodeNumber(scopedNames.size);
    if (!isProduction) {
      scopedName += `__${className}`;
    }

    scopedNames.set(key, scopedName);
  }
  return scopedNames.get(key);
}

module.exports = {
  generateName,
};
