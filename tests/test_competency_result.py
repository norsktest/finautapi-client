"""Tests for the competency result resource.

The payloads mirror what the server's CompetencyResultCreateSerializer
requires (finautapi/api/competency_result.py): goal and reward_type are
hyperlinks, and the list filter for one user is encoded_userid.
"""

import datetime
import json
from urllib.parse import parse_qs, urlparse

import pytest
import responses

from finautapi_client import FinAutAPIClient
from finautapi_client.exceptions import FinAutAPIException

BASE = 'https://api.norsktest.no/finautapi/v1/'
URL = BASE + 'competency_result/'


@pytest.fixture
def client():
    responses.add(responses.POST, 'https://api.norsktest.no/o/token/',
                  json={'access_token': 't', 'token_type': 'Bearer',
                        'expires_in': 3600, 'scope': 'read write'})
    return FinAutAPIClient('test_id', 'test_secret')


def _completion(**overrides):
    kwargs = dict(
        goal=12,
        reward_type=3,
        finished='2026-11-16',
        value=2,
        courseinfo='Etikk og god skikk 2026',
        content_responsible='Kari Nordmann',
        external_system='MyLMS',
        external_id='completion-4711',
    )
    kwargs.update(overrides)
    return kwargs


def _posted():
    return json.loads(responses.calls[-1].request.body)


def _query():
    return parse_qs(urlparse(responses.calls[-1].request.url).query)


@responses.activate
def test_record_completion_sends_what_the_server_requires(client):
    responses.add(responses.POST, URL, json={'id': 1}, status=201)

    result = client.competency_results.record_completion('N3F2A', **_completion())

    assert result == {'id': 1}
    assert _posted() == {
        'user': 'N3F2A',
        'goal': BASE + 'goals/12/',
        'reward_type': BASE + 'reward_types/3/',
        'finished': '2026-11-16',
        'value': 2,
        'courseinfo': 'Etikk og god skikk 2026',
        'content_responsible': 'Kari Nordmann',
        'external_system': 'MyLMS',
        'external_id': 'completion-4711',
    }


@responses.activate
def test_record_completion_passes_urls_through(client):
    responses.add(responses.POST, URL, json={'id': 1}, status=201)
    goal = 'https://api.norsktest.no/finautapi/v1/goals/7/'

    client.competency_results.record_completion(
        'N3F2A', **_completion(goal=goal, reward_type='5'))

    assert _posted()['goal'] == goal
    assert _posted()['reward_type'] == BASE + 'reward_types/5/'


@pytest.mark.parametrize('finished', [
    datetime.date(2026, 11, 16),
    datetime.datetime(2026, 11, 16, 13, 45),  # time part must be dropped
])
@responses.activate
def test_record_completion_formats_dates(client, finished):
    responses.add(responses.POST, URL, json={'id': 1}, status=201)

    client.competency_results.record_completion(
        'N3F2A', **_completion(finished=finished))

    assert _posted()['finished'] == '2026-11-16'


def test_record_completion_requires_every_field(client):
    with pytest.raises(TypeError):
        client.competency_results.record_completion('N3F2A', goal=12)


@responses.activate
def test_list_filters_by_encoded_userid(client):
    responses.add(responses.GET, URL, json=[])

    client.competency_results.list(
        encoded_userid='N3F2A', goal='LIKOFF26',
        from_date=datetime.date(2026, 1, 1))

    assert _query() == {'encoded_userid': ['N3F2A'], 'goal': ['LIKOFF26'],
                        'from_date': ['2026-01-01']}


@responses.activate
def test_list_accepts_old_encrypted_userid_name(client):
    # The server only knows encoded_userid; the old parameter name was
    # silently ignored and returned every subordinate's results.
    responses.add(responses.GET, URL, json=[])

    client.competency_results.list(encrypted_userid='N3F2A')

    assert _query() == {'encoded_userid': ['N3F2A']}


@responses.activate
def test_list_without_filters_sends_no_params(client):
    responses.add(responses.GET, URL, json=[])

    client.competency_results.list()

    assert _query() == {}


@responses.activate
def test_duplicate_completion_raises_with_status_400(client):
    # the API's answer for an external_system + external_id + goal that is
    # already registered
    responses.add(responses.POST, URL, status=400, json={
        'non_field_errors': ['The fields external_system, external_id, goal must make a unique set.']})

    with pytest.raises(FinAutAPIException) as raised:
        client.competency_results.record_completion('N3F2A', **_completion())
    assert raised.value.status_code == 400
    assert 'unique set' in str(raised.value)
