module.exports = {
  root: true,
  parserOptions: {
    ecmaVersion: 2017,
  },
  plugins: ['prettier', 'import-helpers'],
  extends: ['simplabs', 'simplabs/plugins/ember', 'prettier'],
  rules: {
    'ember/local-modules': 'off',
    'ember/order-in-components': 'off',
    'ember/order-in-controllers': 'off',
    'ember/order-in-models': 'off',
    'ember/order-in-routes': 'off',

    'prettier/prettier': 'error',

    'import-helpers/order-imports': [
      'error',
      {
        'newlines-between': 'always',
        groups: [
          'builtin',
          // Testing modules
          ['/^qunit/', '/^ember-qunit/', '/^@ember/test-helpers/', '/^ember-exam/'],
          // Ember.js modules
          ['/^ember$/', '/^@ember/', '/^ember-data/'],
          ['external'],
          [`/^${require('./package.json').name}\\//`, 'internal'],
          ['parent', 'sibling', 'index'],
        ],
        alphabetize: { order: 'asc', ignoreCase: true },
      },
    ],
  },
  overrides: [
    // node files
    {
      files: [
        '.eslintrc.js',
        '.template-lintrc.js',
        'ember-cli-build.js',
        'testem.js',
        'config/**/*.js',
        'lib/*/index.js',
      ],
      parserOptions: {
        sourceType: 'script',
        ecmaVersion: 2015,
      },
      env: {
        browser: false,
        node: true,
      },
    },
  ],
};
