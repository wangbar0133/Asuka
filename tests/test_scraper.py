"""Scraper tests — fully mocked, no network access and no real API keys."""
import pytest

from scraper import scraper as scraper_module
from scraper.scraper import Scraper

ADDRESS = "0x" + "ab" * 20


class FakeResponse:
    def __init__(self, payload, status_code=200):
        self._payload = payload
        self.status_code = status_code

    def json(self):
        return self._payload


def _make_scraper(tmp_path, monkeypatch, payload):
    def fake_get(url, headers=None):
        assert ADDRESS in url
        assert "test-key" in url
        return FakeResponse(payload)

    monkeypatch.setattr(scraper_module.requests, "get", fake_get)
    scraper = Scraper(chainType="ETH", apiKey="test-key")
    scraper.tmpPath = str(tmp_path) + "/"
    return scraper


def test_unsupported_chain():
    with pytest.raises(ValueError, match="Unsupport chain type"):
        Scraper(chainType="BSC", apiKey="test-key")


def test_get_source_code_writes_files(tmp_path, monkeypatch):
    payload = {
        "message": "OK",
        "result": [{"SourceCode": "contract X {}", "ContractName": "X"}],
    }
    scraper = _make_scraper(tmp_path, monkeypatch, payload)

    folder = scraper.get_source_code(ADDRESS)
    assert folder == str(tmp_path) + "/" + ADDRESS
    written = tmp_path / ADDRESS / "X.sol"
    assert written.read_text(encoding="utf-8") == "contract X {}"


def test_get_source_code_reuses_cache(tmp_path, monkeypatch):
    payload = {"message": "OK", "result": []}
    scraper = _make_scraper(tmp_path, monkeypatch, payload)
    (tmp_path / ADDRESS).mkdir()

    # folder already exists -> returns immediately, requests.get never called
    assert scraper.get_source_code(ADDRESS) == str(tmp_path) + "/" + ADDRESS


def test_not_open_source_raises(tmp_path, monkeypatch):
    scraper = _make_scraper(tmp_path, monkeypatch, {"message": "NOTOK"})
    with pytest.raises(ValueError, match="NOT open source"):
        scraper.get_source_code(ADDRESS)


def test_network_error_raises(tmp_path, monkeypatch):
    def broken_get(url, headers=None):
        raise ConnectionError("boom")

    monkeypatch.setattr(scraper_module.requests, "get", broken_get)
    scraper = Scraper(chainType="ETH", apiKey="test-key")
    scraper.tmpPath = str(tmp_path) + "/"
    with pytest.raises(Exception, match="Net err!"):
        scraper.get_source_code(ADDRESS)


def test_http_error_status_raises(tmp_path, monkeypatch):
    scraper = _make_scraper(tmp_path, monkeypatch, None)
    monkeypatch.setattr(
        scraper_module.requests,
        "get",
        lambda url, headers=None: FakeResponse({}, status_code=500),
    )
    with pytest.raises(ValueError, match="Can't get source code from address"):
        scraper.get_source_code(ADDRESS)


def test_missing_result_key_raises(tmp_path, monkeypatch):
    scraper = _make_scraper(tmp_path, monkeypatch, {"message": "OK"})
    with pytest.raises(ValueError, match="Can't get source code!"):
        scraper.get_source_code(ADDRESS)


@pytest.mark.parametrize("field", ["SourceCode", "ContractName"])
def test_non_string_result_field_raises(tmp_path, monkeypatch, field):
    result = {"message": "OK", "result": [{"SourceCode": "contract X {}",
                                           "ContractName": "X"}]}
    result["result"][0][field] = 12345
    scraper = _make_scraper(tmp_path, monkeypatch, result)
    with pytest.raises(ValueError, match="Can't get source code!"):
        scraper.get_source_code(ADDRESS)
