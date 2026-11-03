import importlib.util
import os
from io import BytesIO
from pathlib import Path

import pytest
from PIL import Image


os.environ.setdefault("TABLE_NAME", "test-table")

HANDLER_PATH = Path(__file__).parents[1] / "lambda" / "handler.py"
SPEC = importlib.util.spec_from_file_location("lambda_handler", HANDLER_PATH)
handler = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(handler)


def image_bytes(color, size=(100, 100), image_format="PNG"):
    image = Image.new("RGB", size, color)
    buffer = BytesIO()
    image.save(buffer, format=image_format)
    return buffer.getvalue()


def test_analyze_image_returns_expected_metadata():
    result = handler.analyze_image(image_bytes((128, 128, 128)))

    assert result["format"] == "PNG"
    assert result["width"] == 100
    assert result["height"] == 100
    assert result["average_color_rgb"] == [128, 128, 128]
    assert result["quality"] in {"good", "acceptable", "needs_review"}


def test_analyze_image_rejects_oversized_input(monkeypatch):
    monkeypatch.setattr(handler, "MAX_IMAGE_BYTES", 10)

    with pytest.raises(ValueError, match="exceeds"):
        handler.analyze_image(image_bytes((0, 0, 0)))
