import pytest
from bs_service import BSService, BSServiceConfig, InvalidInputException, BSLLMOutput

@pytest.fixture
def bs_service() -> BSService:
    return BSService(BSServiceConfig())

def test_scrape_url(bs_service: BSService) -> None:
    url = "http://example.com"
    content = bs_service.scrape_url(url)
    assert isinstance(content, str)
    assert len(content) > 0

def test_calculate_bullshit_with_text(bs_service: BSService) -> None:
    text = "This is a test text."
    result = bs_service.calculate_bullshit(text)
    assert isinstance(result, BSLLMOutput)
    assert 0 <= result.score < 10
    assert isinstance(result.explanation, str)

def test_calculate_bullshit_with_url(bs_service: BSService) -> None:
    url = "http://example.com"
    result = bs_service.calculate_bullshit(url)
    assert isinstance(result, BSLLMOutput)
    assert 0 <= result.score < 10
    assert isinstance(result.explanation, str)

def test_calculate_bullshit_with_invalid_input(bs_service: BSService) -> None:
    with pytest.raises(InvalidInputException):
        bs_service.calculate_bullshit("")

def test_is_url(bs_service: BSService) -> None:
    assert bs_service.is_url("https://example.com") is True, "Failed for https url"
    