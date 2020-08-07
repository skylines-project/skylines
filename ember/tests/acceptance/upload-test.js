import { visit, currentURL, click, triggerEvent } from '@ember/test-helpers';
import { setupApplicationTest } from 'ember-qunit';
import { module, test } from 'qunit';

import { setupMirage } from 'ember-cli-mirage/test-support';

import * as MockFlight from 'skylines/mirage/vcr/flights/87296';
import { IGC } from 'skylines/mirage/vcr/flights/94bf14k1';

import { authenticateAs } from '../test-helpers/auth';
import { setupMockCookies } from '../test-helpers/cookies';

module('Acceptance | flight upload', function (hooks) {
  setupApplicationTest(hooks);
  setupMirage(hooks);
  setupMockCookies(hooks);

  test('flights can be uploaded', async function (assert) {
    let user = this.server.create('user', {
      firstName: 'John',
      lastName: 'Doe',
    });

    await authenticateAs(user);

    this.server.post('/api/flights/upload/', {
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

    this.server.post('/api/flights/upload/verify', {});

    this.server.get('/api/flights/87296/json', MockFlight.JSON);
    this.server.get('/api/flights/87296', MockFlight.EXTENDED);

    await visit('/flights/upload');
    assert.equal(currentURL(), '/flights/upload');

    let blob = new Blob([IGC], { type: 'text/plain' });
    let file = new File([blob], '94bf14k1.igc', { type: blob.type });

    await triggerEvent('[data-test-files]', 'change', { files: [file] });
    await click('[data-test-submit-button]');
    assert.equal(currentURL(), '/flights/upload');

    await click('[data-test-publish-button]');
    assert.equal(currentURL(), '/flights/87296');
  });

  test('unauthenticated visit redirects to the login page', async function (assert) {
    await visit('/flights/upload');
    assert.equal(currentURL(), '/login');
  });
});
