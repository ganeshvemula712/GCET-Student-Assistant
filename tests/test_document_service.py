import pytest

from fastapi import HTTPException, UploadFile

from backend.app.services.documents import process_document


@pytest.mark.asyncio
async def test_process_document_rejects_non_pdf(
    db_session,
):

    file = UploadFile(
        filename="test.txt",
        file=None,
        headers={
            "content-type": "text/plain"
        },
    )

    with pytest.raises(HTTPException) as error:

        await process_document(
            file=file,
            db=db_session,
        )

    assert error.value.status_code == 400

    assert "Unsupported file format" in error.value.detail