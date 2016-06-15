module.exports = {
  root: true,
  parserOptions: {
    ecmaVersion: 6,
    sourceType: 'module'
  },
  extends: 'eslint:recommended',
  env: {
    'browser': true,
  },
  rules: {
    'comma-dangle': [2, 'always-multiline'],
  },
};
