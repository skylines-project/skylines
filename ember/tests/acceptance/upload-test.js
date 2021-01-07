import { visit, currentURL, click, triggerEvent, settled, waitFor } from '@ember/test-helpers';
import { module, test } from 'qunit';

import { defer } from 'rsvp';

import { t } from 'ember-intl/test-support';

import * as MockFlight from 'skylines/mirage/vcr/flights/87296';
import { IGC } from 'skylines/mirage/vcr/flights/94bf14k1';

import { setupApplicationTest } from '../test-helpers';
import { authenticateAs } from '../test-helpers/auth';

module('Acceptance | flight upload', function (hooks) {
  setupApplicationTest(hooks);

  test('flights can be uploaded', async function (assert) {
    let user = this.server.create('user', {
      firstName: 'John',
      lastName: 'Doe',
    });

    await authenticateAs(user);

    let deferred = defer();
    this.server.post('/api/flights/upload/', deferred.promise);

    this.server.post('/api/flights/upload/verify', {});

    this.server.get('/api/flights/87296/json', MockFlight.JSON);
    this.server.get('/api/flights/87296', MockFlight.EXTENDED);

    await visit('/flights/upload');
    assert.equal(currentURL(), '/flights/upload');
    assert.dom('[data-test-files]').isEnabled();
    assert.dom('[data-test-pilot] .ember-power-select-trigger').doesNotHaveAria('disabled');
    assert.dom('[data-test-submit-button]').isDisabled().hasText(t('upload'));

    let file = new File([IGC], '94bf14k1.igc', { type: 'text/plain' });
    await triggerEvent('[data-test-files]', 'change', { files: [file] });
    assert.dom('[data-test-submit-button]').isEnabled().hasText(t('upload'));

    click('[data-test-submit-button]');
    await waitFor('[data-test-upload-form="uploading"]');
    assert.dom('[data-test-files]').isDisabled();
    assert.dom('[data-test-pilot] .ember-power-select-trigger').hasAria('disabled', 'true');
    assert.dom('[data-test-submit-button]').isDisabled().hasText(t('uploading'));

    deferred.resolve({
      club_members: [],
      aircraft_models: [],
      results: [
        {
          status: 0,
          cacheKey: 'foobar42',
          flight: {
            pilotName: null,
            takeoffAirport: null,
            registration: 'LY-KDR',
            speed: 30.63035019455253,
            id: 87296,
            privacyLevel: 2,
            takeoffTime: '2011-06-18T09:11:23+00:00',
            score: 9.073321994774085,
            scoreEndTime: '2011-06-18T09:15:40+00:00',
            copilot: null,
            timeCreated: '2020-07-12T12:34:56+00:00',
            scoreStartTime: '2011-06-18T09:11:23+00:00',
            club: null,
            scoreDate: '2011-06-18T09:11:23',
            landingTime: '2011-06-18T09:15:40+00:00',
            rawScore: 9.073321994774085,
            copilotName: null,
            pilot: null,
            distance: 7872,
            igcFile: {
              date: '2011-06-18',
              model: 'ASK13',
              registration: 'LY-KDR',
              competitionId: null,
              filename: '94bf14k1.igc',
            },
            landingAirport: null,
            triangleDistance: 4003,
            model: null,
            competitionId: null,
          },
          name: '94bf14k1.igc',
          trace: {
            barogram_h:
              'yG?K@?????????????????????????????????????D?????EEEEIEKOIMSMIKOUWKOOOGUIEg@c@SUEKIKEEKI[]_@a@WSGYQk@',
            igc_end_time: '2011-06-18T09:15:40+00:00',
            enl: '??????????????????????????????????????????????????????????????????????????????????????????????',
            elevations_h:
              'n}@?????????????????????????????????????????????????????????????????????????????????????????????',
            igc_start_time: '2011-06-18T09:07:49+00:00',
            barogram_t:
              'ie_AIIIIIIIIIIIIIIKIIIIKIKIIIIIIIIIIIIIIIKIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIMIIIIIIIIIIIIIIIIIIIIII',
          },
          airspaces: [],
        },
      ],
    });
    await settled();
    assert.equal(currentURL(), '/flights/upload');

    await click('[data-test-publish-button]');
    assert.equal(currentURL(), '/flights/87296');
  });

  test('unauthenticated visit redirects to the login page', async function (assert) {
    await visit('/flights/upload');
    assert.equal(currentURL(), '/login');
  });
});
