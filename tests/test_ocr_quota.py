import pytest
from unittest.mock import MagicMock, patch
from backend.app.services.ocr import (
    extract_document_pages,
    call_gemini_ocr_batch_with_retry,
    GeminiQuotaExhaustedError,
    GeminiRateLimitError,
)
from google.genai import types

def test_text_pdf_requires_zero_ocr_requests(monkeypatch):
    """Test that PDFs with native text require zero Gemini OCR API calls."""
    mock_pdf = MagicMock()
    mock_pdf.__len__.return_value = 2

    mock_page1 = MagicMock()
    mock_page1.get_text.return_value = "This is native PDF text for page 1 that is long enough to bypass OCR completely."

    mock_page2 = MagicMock()
    mock_page2.get_text.return_value = "This is native PDF text for page 2 that is also long enough to bypass OCR completely."

    mock_pdf.__getitem__.side_effect = [mock_page1, mock_page2]

    with patch("pymupdf.open", return_value=mock_pdf):
        with patch("backend.app.services.ocr.call_gemini_ocr_batch_with_retry") as mock_ocr_call:
            page_count, pages = extract_document_pages(b"%PDF-sample", "test_native.pdf")
            assert page_count == 2
            assert len(pages) == 2
            assert pages[0][1].startswith("This is native PDF text for page 1")
            assert pages[1][1].startswith("This is native PDF text for page 2")
            # Verify ZERO Gemini OCR calls were made
            mock_ocr_call.assert_not_called()

def test_scanned_pdf_batches_pages_into_single_gemini_call(monkeypatch):
    """Test that multiple scanned pages are batched into fewer Gemini OCR calls."""
    mock_pdf = MagicMock()
    mock_pdf.__len__.return_value = 4

    pages = []
    for i in range(4):
        p = MagicMock()
        p.get_text.return_value = ""  # Empty text = scanned
        pix = MagicMock()
        pix.tobytes.return_value = b"jpeg_bytes"
        p.get_pixmap.return_value = pix
        pages.append(p)

    mock_pdf.__getitem__.side_effect = lambda idx: pages[idx]

    mock_gemini_res = MagicMock()
    mock_gemini_res.text = "--- PAGE 1 ---\nText 1\n--- PAGE 2 ---\nText 2\n--- PAGE 3 ---\nText 3\n--- PAGE 4 ---\nText 4"

    with patch("pymupdf.open", return_value=mock_pdf):
        with patch("backend.app.services.ocr.gemini_client.models.generate_content", return_value=mock_gemini_res) as mock_gen:
            page_count, extracted = extract_document_pages(b"%PDF-scanned", "scanned_doc.pdf")
            assert page_count == 4
            assert len(extracted) == 4
            # 4 pages batched into OCR_BATCH_SIZE (4) -> exactly 1 Gemini API call
            assert mock_gen.call_count == 1

def test_temporary_429_retries_and_succeeds():
    """Test temporary 429 rate limits retry with backoff and succeed."""
    mock_gemini_res = MagicMock()
    mock_gemini_res.text = "--- PAGE 1 ---\nRecovered text after 429"

    part = types.Part.from_bytes(data=b"img", mime_type="image/jpeg")

    with patch("time.sleep"):
        with patch(
            "backend.app.services.ocr.gemini_client.models.generate_content",
            side_effect=[Exception("429 RESOURCE_EXHAUSTED Rate limit exceeded"), mock_gemini_res],
        ) as mock_gen:
            results = call_gemini_ocr_batch_with_retry([(1, part)])
            assert len(results) == 1
            assert results[0][1] == "Recovered text after 429"
            assert mock_gen.call_count == 2

def test_daily_quota_exhaustion_stops_retries():
    """Test daily quota exhaustion raises GeminiQuotaExhaustedError immediately without retrying."""
    quota_err_msg = (
        "429 RESOURCE_EXHAUSTED Quota exceeded for metric: "
        "generativelanguage.googleapis.com/generate_content_free_tier_requests model: gemini-2.5-flash limit: 20"
    )
    part = types.Part.from_bytes(data=b"img", mime_type="image/jpeg")

    with patch(
        "backend.app.services.ocr.gemini_client.models.generate_content",
        side_effect=Exception(quota_err_msg),
    ) as mock_gen:
        with pytest.raises(GeminiQuotaExhaustedError):
            call_gemini_ocr_batch_with_retry([(1, part)])
        # Must fail fast on 1st attempt without retrying
        assert mock_gen.call_count == 1
