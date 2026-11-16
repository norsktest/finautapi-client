"""Tests for paging and the exam result helpers.

The server's /results/ only answers with persnr or from_date (an empty
list otherwise) and honours employee_alias only inside a from_date query.
"""
from urllib.parse import parse_qs, urlparse

import pytest
import responses

from finautapi_client import FinAutAPIClient

URL = 'https://api.norsktest.no/finautapi/v1/results/'


@pytest.fixture
def client():
    responses.add(responses.POST, 'https://api.norsktest.no/o/token/',
                  json={'access_token': 't', 'expires_in': 3600})
    return FinAutAPIClient('test_id', 'test_secret')


def _queries():
    return [parse_qs(urlparse(c.request.url).query)
            for c in responses.calls if c.request.url.startswith(URL)]


@responses.activate
def test_get_all_follows_pages(client):
    responses.add(responses.GET, URL, json={'count': 3, 'next': URL + '?page=2',
                                            'results': [{'id': 1}, {'id': 2}]})
    responses.add(responses.GET, URL, json={'count': 3, 'next': None,
                                            'results': [{'id': 3}]})

    assert client.get_all('results/', {'persnr': '1'}) == [{'id': 1}, {'id': 2}, {'id': 3}]
    assert _queries() == [{'persnr': ['1']}, {'persnr': ['1'], 'page': ['2']}]


@responses.activate
def test_get_all_accepts_an_unpaginated_list(client):
    responses.add(responses.GET, URL, json=[{'id': 1}])

    assert client.get_all('results/') == [{'id': 1}]


@responses.activate
def test_user_results_by_persnr(client):
    responses.add(responses.GET, URL, json=[{'id': 1}])

    assert client.results.get_user_results(persnr='12345678901') == [{'id': 1}]
    assert _queries() == [{'persnr': ['12345678901']}]


@responses.activate
def test_user_results_by_employee_alias_uses_from_date(client):
    responses.add(responses.GET, URL, json=[])

    client.results.get_user_results(employee_alias='EMP1')

    assert _queries() == [{'employee_alias': ['EMP1'], 'from_date': ['2000-01-01']}]


def test_user_results_needs_an_identifier(client):
    with pytest.raises(ValueError):
        client.results.get_user_results()


@responses.activate
def test_recent_results_sends_from_date(client):
    responses.add(responses.GET, URL, json=[])

    client.results.get_recent_results(days=7)

    (query,) = _queries()
    assert list(query) == ['from_date']
