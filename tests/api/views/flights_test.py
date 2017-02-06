import base64

import pytest
from datetime import date

from flask import json

from skylines.model import User, Club, Flight, IGCFile
from werkzeug.datastructures import Headers
from tests.data import add_fixtures


@pytest.fixture
def club_1():
    return Club(name=u'LV Aachen')


@pytest.fixture
def club_2():
    return Club(name=u'Sportflug Niederberg')


@pytest.fixture
def user_with_club(club_1):
    return User(first_name=u'John', last_name=u'Smith',
                email_address='john@smith.com', password='123456', club=club_1)


@pytest.fixture
def user_with_same_club(club_1):
    return User(first_name=u'Fred', last_name=u'Bloggs',
                email_address='fred@bloggs.com', password='123456', club=club_1)


@pytest.fixture
def user_with_other_club(club_2):
    return User(first_name=u'Joe', last_name=u'Bloggs',
                email_address='joe@bloggs.com', password='123456', club=club_2)


@pytest.fixture
def user_without_club():
    return User(first_name=u'Club', last_name=u'Less',
                email_address='club@less.com', password='123456')


@pytest.fixture
def user_without_club_2():
    return User(first_name=u'No', last_name=u'Club',
                email_address='no@club.com', password='123456')


@pytest.fixture
def igc(user_with_club):
    return IGCFile(owner=user_with_club,
                   filename='simple.igc', md5='ebc87aa50aec6a6667e1c9251a68a90e', date_utc=date(2011, 6, 18))


@pytest.fixture
def flight(igc, user_with_club):
    return Flight(pilot=user_with_club, co_pilot=None, date_local='2011-06-18', takeoff_time='2011-06-18 09:11:23',
                  landing_time='2011-06-18 09:15:40', timestamps='', igc_file=igc,
                  locations='0102000020E6100000380000000D43014D84FD384011E8E00B933D4B40D80CA06485FD38402B831180'
                            '923D4B40D80CA06485FD3840F64CB097933D4B401C70B3EA73FD384034A1DD93873D4B40CF5D555555'
                            'FD38409FCCD32B653D4B4026FD00032EFD3840DFDF34EF383D4B40E817550BFFFC3840D530EADF083D'
                            '4B404CE4B256C7FC3840CC819FD0D83C4B40B0B010A28FFC38408F9CF3D8A93C4B4069AD98966BFC38'
                            '4003E6B5847C3C4B40C86A105839FC38402A5EE6D3503C4B40BFBBC54809FC384006146B50213C4B40'
                            '5BCD6A06CBFB384095F85D70F33B4B40614BD2948AFB38409CC677C1CD3B4B4037A2BEC445FB38403B'
                            '28CF41AA3B4B40AEAAB437F8FA3840772C4A7B833B4B4024B3AAAAAAFA38407FFA63CC5D3B4B40FE18'
                            '7D6460FA384085C87D1D383B4B40B375A0D306FA38400A8FA429153B4B40DA5C5227A0F9384027E908'
                            '65F43A4B4093C85B2041F93840C64A60E5D03A4B40E4C7A248E4F8384099E2184EAC3A4B4002918888'
                            '88F838406D7AD1B6873A4B40FD5FA50718F838405AADBA93623A4B40C5F8609EA8F73840AB3D80B740'
                            '3A4B40585BBB4C3AF738409261830A213A4B40B887B412CDF63840484F2575023A4B405508DBD453F6'
                            '3840307328C8E2394B40C3618638D6F53840E560CA32C4394B404CA614D372F538402065456C9D394B'
                            '403EE8E33948F5384095AE071870394B40E9B7B99034F538402293FA3742394B404906B04D3DF53840'
                            'D7809CA223394B401D101870A9F538401FF395B20C394B40AA38057E67F6384023027C3C07394B40D4'
                            '9494405DF738409CEBA26D0F394B40C51A5E951EF838407423C05B20394B403A674EF6BCF838407B82'
                            '58A835394B4051D4C99E17F9384051BA759646394B4001B3857FFEF838408CE0EDC695394B40657FE3'
                            'CAC6F838407D44BA24E1394B404E1268226CF8384005EC11EF133A4B4053FF50B5F0F7384013AA4288'
                            '3E3A4B40610A065C6AF73840A36F6666663A4B4063578A69B9F63840EF81C4FB843A4B406DC2DA8AFD'
                            'F538406D7AD1B6873A4B4014D04E653EF53840C05A499D803A4B404953345B8CF43840B4ECCAC6703A'
                            '4B4033553AB7F6F338402F9525BF583A4B40FFFCDBD781F33840E482C7293A3A4B40E88F602F27F338'
                            '4083E41EAA163A4B40AEB99AC1F2F238400DBA2B40EE394B405A897018DFF238407CF40762C6394B40'
                            'B4C8804BEDF23840EB2EE4839E394B409C7D029A08F33840E4CF4B3789394B40B3EA7D4263F338403D'
                            'BFA9A77C394B40')


def authenticate_with(user):
    password = '123456'

    headers = Headers()
    headers.add('Authorization', 'Basic ' + base64.b64encode(user.email_address + ':' + password))

    return headers


def change_pilots(client, flight, auth_user, pilot=None, copilot=None, pilot_name=None, copilot_name=None):
    headers = authenticate_with(auth_user)

    data = {}
    if pilot: data['pilotId'] = pilot.id
    if copilot: data['copilotId'] = copilot.id
    if pilot_name: data['pilotName'] = pilot_name
    if copilot_name: data['copilotName'] = copilot_name

    flight_url = '/flights/{}/'.format(flight.id)

    return client.post(flight_url, headers=headers, data=json.dumps(data), content_type='application/json')


def test_pilot_changing_correct_with_co(db_session, client, flight, user_with_club, user_with_same_club):
    """ Pilot is changing copilot to user from same club. """

    add_fixtures(db_session, flight, user_with_club, user_with_same_club)

    response = change_pilots(client, flight, auth_user=user_with_club,
                             pilot=user_with_club, copilot=user_with_same_club)

    assert response.status_code == 200


def test_pilot_changing_disowned_flight(db_session, client, flight,
                                        user_with_club, user_with_same_club, user_with_other_club):
    """ Unrelated user is trying to change pilots. """

    add_fixtures(db_session, flight, user_with_club, user_with_same_club, user_with_other_club)

    response = change_pilots(client, flight, auth_user=user_with_same_club,
                             pilot=user_with_club, copilot=user_with_other_club)

    assert response.status_code == 403


def test_pilot_changing_disallowed_pilot(db_session, client, flight, user_with_club, user_with_other_club):
    """ Pilot is trying to change pilot to user from different club. """

    add_fixtures(db_session, flight, user_with_club, user_with_other_club)

    response = change_pilots(client, flight, auth_user=user_with_club,
                             pilot=user_with_other_club, copilot=user_with_club)

    assert response.status_code == 422


def test_pilot_changing_disallowed_copilot(db_session, client, flight, user_with_club, user_with_other_club):
    """ Pilot is trying to change copilot to user from different club. """

    add_fixtures(db_session, flight, user_with_club, user_with_other_club)

    response = change_pilots(client, flight, auth_user=user_with_club,
                             pilot=user_with_club, copilot=user_with_other_club)

    assert response.status_code == 422


def test_pilot_changing_same_pilot_and_co(db_session, client, flight, user_with_club):
    """ Pilot is trying to change copilot to the same as pilot. """

    add_fixtures(db_session, flight, user_with_club)

    response = change_pilots(client, flight, auth_user=user_with_club,
                             pilot=user_with_club, copilot=user_with_club)

    assert response.status_code == 422


def test_pilot_changing_pilot_and_co_null(db_session, client, flight, user_with_club):
    """ Pilot is changing pilot and copilot to unknown user accounts. """

    add_fixtures(db_session, flight, user_with_club)

    response = change_pilots(client, flight, auth_user=user_with_club,
                             pilot_name='foo', copilot_name='bar')

    assert response.status_code == 200


def test_pilot_changing_clubless_co(db_session, client, flight, user_with_club, user_without_club):
    """ Pilot is trying to change copilot to user without club. """

    add_fixtures(db_session, flight, user_with_club, user_without_club)

    response = change_pilots(client, flight, auth_user=user_with_club,
                             pilot=user_with_club, copilot=user_without_club)

    assert response.status_code == 422


def test_pilot_changing_clubless_pilot_and_co(db_session, client, flight, user_without_club, user_without_club_2):
    """ Pilot without club is trying to change copilot to user without club. """

    flight.pilot = user_without_club
    add_fixtures(db_session, flight, user_without_club, user_without_club_2)

    response = change_pilots(client, flight, auth_user=user_without_club,
                             pilot=user_without_club, copilot=user_without_club_2)

    assert response.status_code == 422
