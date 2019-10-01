module.exports = {
  root: true,
  parserOptions: {
    ecmaVersion: 2017,
  },
  plugins: ['prettier', 'import-helpers'],
  extends: ['simplabs', 'simplabs/plugins/ember', 'prettier'],
  rules: {
    'ember/avoid-leaking-state-in-ember-objects': 'error',
    'ember/avoid-leaking-state-in-components': 'off',

    'ember/local-modules': 'off',
    'ember/order-in-components': 'off',
    'ember/order-in-controllers': 'off',
    'ember/order-in-models': 'off',
    'ember/order-in-routes': 'off',

    'prettier/prettier': 'error',

    'import-helpers/order-imports': [
      'error',
      {
        newlinesBetween: 'always',
        groups: [
          '/^(assert|async_hooks|buffer|child_process|cluster|console|constants|crypto|dgram|dns|domain|events|fs|http|http2|https|inspector|module|net|os|path|perf_hooks|process|punycode|querystring|readline|repl|stream|string_decoder|timers|tls|trace_events|tty|url|util|v8|vm|zli)/',
          // Testing modules
          ['/^qunit/', '/^ember-qunit/', '/^@ember/test-helpers/', '/^ember-exam/'],
          // Ember.js modules
          ['/^ember$/', '/^@ember/', '/^ember-data/'],
          ['module'],
          [`/^${require('./package.json').name}\\//`],
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
