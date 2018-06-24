module.exports = {
  parserOptions: {
    ecmaVersion: 2017,
  },
  extends: ['simplabs/configs/ember-qunit', 'prettier'],
  env: {
    embertest: null,
  },
  rules: {
    'prettier/prettier': 'error',
  },
};
