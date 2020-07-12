export default function () {
  this.passthrough('/translations/**');

  this.get('/api/locale', { locale: 'en' });
}
