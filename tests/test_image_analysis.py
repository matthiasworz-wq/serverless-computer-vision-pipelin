import importlib.util
import os
from io import BytesIO
from pathlib import Path

from PIL import Image


os.environ["TABLE_NAME"] = "test-table"
handler_path = Path(__file__).parents[1] / "lambda" / "handler.py"
spec = importlib.util.spec_from_file_location("lambda_handler", handler_path)
handler = importlib.util.module_from_spec(spec)
spec.loader.exec_module(handler)


def test_analyze_image_returns_quality_metrics():
    image = Image.new("RGB", (800, 600), (120, 130, 140))
    buffer = BytesIO()
    image.save(buffer, format="JPEG")

    result = handler.analyze_image(buffer.getvalue())

    assert result["format"] == "JPEG"
    assert result["width"] == 800
    assert result["height"] == 600
    assert result["quality"] in {"good", "acceptable", "needs_review"}
    assert "sharpness" in result
