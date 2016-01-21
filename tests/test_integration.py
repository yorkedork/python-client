# coding: utf-8
from coreapi import get_client, action, get, load, dump, Link, ErrorMessage
import coreapi
import requests
import pytest


encoded = (
    b'{"_type":"document","_meta":{"url":"http://example.org"},'
    b'"a":123,"next":{"_type":"link"}}'
)


@pytest.fixture
def document():
    return load(encoded)


class MockResponse(object):
    def __init__(self, content):
        self.content = content
        self.headers = {}
        self.url = 'http://example.org'
        self.status_code = 200


# Basic integration tests.

def test_load():
    assert load(encoded) == {
        "a": 123,
        "next": Link(url='http://example.org')
    }


def test_dump(document):
    content_type, content = dump(document)
    assert content_type == 'application/vnd.coreapi+json'
    assert content == encoded


def test_get(monkeypatch):
    def mockreturn(method, url, headers):
        return MockResponse(b'{"_type": "document", "example": 123}')

    monkeypatch.setattr(requests, 'request', mockreturn)

    doc = get('http://example.org')
    assert doc == {'example': 123}


def test_follow(monkeypatch, document):
    def mockreturn(method, url, headers):
        return MockResponse(b'{"_type": "document", "example": 123}')

    monkeypatch.setattr(requests, 'request', mockreturn)

    doc = action(document, ['next'])
    assert doc == {'example': 123}


def test_reload(monkeypatch):
    def mockreturn(method, url, headers):
        return MockResponse(b'{"_type": "document", "example": 123}')

    monkeypatch.setattr(requests, 'request', mockreturn)

    doc = coreapi.Document(url='http://example.org')
    doc = coreapi.reload(doc)
    assert doc == {'example': 123}


def test_error(monkeypatch, document):
    def mockreturn(method, url, headers):
        return MockResponse(b'{"_type": "error", "message": ["failed"]}')

    monkeypatch.setattr(requests, 'request', mockreturn)

    with pytest.raises(ErrorMessage):
        action(document, ['next'])


def test_get_client():
    client = get_client(
        credentials={'example.org': 'abc'},
        headers={'user-agent': 'foo'}
    )

    assert len(client.codecs) == 4
    assert len(client.transports) == 1

    assert client.transports[0].credentials == {'example.org': 'abc'}
    assert client.transports[0].headers == {'user-agent': 'foo'}
