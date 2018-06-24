module.exports = {
  env: {
    node: true,
    browser: false,
  },
  rules: {
    // unfortunate workaround for:
    // ENOENT: no such file or directory, scandir 'skylines/ember/lib/freestyle/app/app/controllers'
    'prettier/prettier': 'off',
  },
};
