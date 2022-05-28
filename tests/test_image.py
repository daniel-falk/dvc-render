import os

import pytest

from dvc_render.image import ImageRenderer

# pylint: disable=missing-function-docstring


@pytest.mark.parametrize(
    "extension, matches",
    (
        (".csv", False),
        (".json", False),
        (".tsv", False),
        (".yaml", False),
        (".jpg", True),
        (".gif", True),
        (".jpeg", True),
        (".png", True),
    ),
)
def test_matches(extension, matches):
    filename = "file" + extension
    assert ImageRenderer.matches(filename, {}) == matches


@pytest.mark.parametrize("html_path", [None, "/output/dir/index.html"])
@pytest.mark.parametrize(
    "src", ["relpath.jpg", "data:image;base64,encoded_image"]
)
def test_render(html_path, src):
    datapoints = [
        {
            "filename": "file.jpg",
            "rev": "workspace",
            "src": src,
        }
    ]

    html = ImageRenderer(datapoints, "file.jpg").generate_html(
        html_path=html_path
    )

    assert "<p>file.jpg</p>" in html
    assert f'<img src="{src}">' in html


@pytest.mark.parametrize(
    "html_path,img_path,expected_path",
    [
        (
            os.path.join("output", "path", "index.html"),
            os.path.join("output", "path", "with", "static", "file.jpg"),
            os.path.join("with", "static", "file.jpg"),
        ),
        (
            os.path.join("output", "one", "path", "index.html"),
            os.path.join("output", "second", "path", "file.jpg"),
            os.path.join("..", "..", "second", "path", "file.jpg"),
        ),
    ],
)
def test_render_evaluate_path(tmp_dir, html_path, img_path, expected_path):
    abs_html_path = tmp_dir / html_path
    abs_img_path = tmp_dir / img_path

    datapoints = [
        {
            "filename": "file.jpg",
            "rev": "workspace",
            "src": str(abs_img_path),
        }
    ]

    html = ImageRenderer(datapoints, "file.jpg").generate_html(
        html_path=abs_html_path
    )

    assert "<p>file.jpg</p>" in html
    assert f'<img src="{expected_path}">' in html


def test_render_empty():
    html = ImageRenderer(None, None).generate_html()
    assert html == ""