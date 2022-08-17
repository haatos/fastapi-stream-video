from __future__ import annotations

import os

from fastapi import FastAPI, status
from fastapi.requests import Request
from fastapi.responses import StreamingResponse


app = FastAPI()


def video_to_chunks(source: str, chunk_size: int, start: int, size: int) -> bytes:
    bytes_read = 0

    with open(source, mode="rb") as stream:
        stream.seek(start)

        while bytes_read < size:
            bytes_to_read = min(chunk_size, size - bytes_read)
            yield stream.read(bytes_to_read)
            bytes_read += bytes_to_read


@app.get("/video")
def stream_video(request: Request):
    chunk_size = 1024 * 1024
    range = request.headers.get("Range")
    start, end = range.replace("bytes=", "").split("-")
    start = int(start)
    end = int(end) if end else start + chunk_size
    source = "red-leaves-in-autumn.mp4"
    total_size = os.path.getsize(source)

    return StreamingResponse(
        content=video_to_chunks(
            source=source, chunk_size=chunk_size, start=start, size=total_size
        ),
        status_code=status.HTTP_206_PARTIAL_CONTENT,
        headers={
            "Accept-Ranges": "bytes",
            "Content-Length": total_size,
            "Content-Range": f"bytes {start}-{start + chunk_size}/{total_size}",
            "Content-Type": "video/mp4",
        },
    )
