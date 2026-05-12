# //////////////////////////////////////////////////////////////////////////////
import pytest
import json
import os
import logging

from src.pgpro_pytest_html_json_extractor import __main__ as prog

# //////////////////////////////////////////////////////////////////////////////


def test_001__extraction_valid_html(tmp_path):
    # 1: Create fake HTML with the desired structure
    content = """
    <html>
        <body>
            <div id="data-container" data-jsonblob='{"result": "passed", "tests": 10}'></div>
            <div class="footer"><a href="pytest-html">v4.0.2</a></div>
        </body>
    </html>
    """
    report = tmp_path / "report.html"
    output = tmp_path / "out.json"
    report.write_text(content, encoding="utf-8")

    # 2. Launch the extractor
    prog.PytestHtmlJsonExtractor.exec(
        input_path=str(report), check_json=True, output_path=str(output), replace=True
    )

    # 3. Check the result
    with open(output, "r") as f:
        data = json.load(f)

    assert data["result"] == "passed"
    assert data["tests"] == 10
    return


# ------------------------------------------------------------------------
# Helper for creating "dirty" HTML files
def create_report(
    path, version="4.0.2", data='{"status": "ok"}', tag_id="data-container"
):
    content = f"""
    <html>
        <body>
            <div id="{tag_id}" data-jsonblob='{data}'></div>
            <p>Report generated on 10-May-2026 at 12:34:40 by <a href="https://pypi.python.org/pypi/pytest-html">pytest-html</a>
                v{version}</p>
        </body>
    </html>
    """
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return


# ------------------------------------------------------------------------
def test_002__unsupported_version(tmp_path):
    # Check for the old version v3.0.0
    report = tmp_path / "old_report.html"
    create_report(report, version="3.0.0")

    with pytest.raises(RuntimeError) as x:
        prog.PytestHtmlJsonExtractor.exec(str(report), True, "out.json", True)

    exc_text = str(x.value)
    assert "unsupported version" in exc_text
    assert "[3.0.0]" in exc_text
    return


# ------------------------------------------------------------------------
@pytest.mark.parametrize(
    "valid_data",
    [
        '{"key": "value"}',
        '{"list": [1, 2, 3], "nested": {"a": 1}}',
        '{"list": [1.5, 2.5, 3.5], "nested": {"a": 1.5}}',
        '{"list": [true, false, true], "nested": {"a": "true"}}',
        "[]",  # An empty list is also valid JSON
    ],
)
def test_003__happy_path(tmp_path, valid_data):
    """We check that everything works when everything is fine."""
    report = tmp_path / "report.html"
    output = tmp_path / "out.json"
    create_report(report, data=valid_data)

    prog.PytestHtmlJsonExtractor.exec(str(report), True, str(output), True)

    with open(output, "r") as f:
        assert f.read() == valid_data
    return


# ------------------------------------------------------------------------
def test_004__unsupported_version_error(tmp_path):
    """Scenario: Version too old."""
    report = tmp_path / "old_report.html"
    create_report(report, version="3.2.0")

    with pytest.raises(RuntimeError, match="unsupported version"):
        prog.PytestHtmlJsonExtractor.exec(str(report), True, "out.json", True)
    return


# ------------------------------------------------------------------------
def test_005__corrupted_json_with_check_enabled(tmp_path):
    """Scenario: JSON is broken and the --check flag is enabled."""
    report = tmp_path / "bad_json.html"
    create_report(report, data='{"key": "no_closing_brace"')  # Ошибка в JSON

    # Должен упасть на json.loads()
    with pytest.raises(json.JSONDecodeError):
        prog.PytestHtmlJsonExtractor.exec(str(report), True, "out.json", True)
    return


# ------------------------------------------------------------------------
def test_006__missing_data_container(tmp_path):
    """Scenario: The required div is missing from the HTML."""
    report = tmp_path / "no_container.html"
    create_report(report, tag_id="wrong-id")

    with pytest.raises(RuntimeError) as x:
        prog.PytestHtmlJsonExtractor.exec(str(report), True, "out.json", True)

    assert "does not countains json data" in str(x.value)
    return


# ------------------------------------------------------------------------
def test_007__output_file_already_exists(tmp_path):
    """Scenario: the file already exists, and the --replace=False flag (mode 'x')."""
    report = tmp_path / "report.html"
    output = tmp_path / "out.json"
    create_report(report)
    output.write_text("existing content")

    with pytest.raises(FileExistsError):
        prog.PytestHtmlJsonExtractor.exec(str(report), True, str(output), replace=False)
    return


# ------------------------------------------------------------------------
def test_008__encoding_stress_test(tmp_path):
    """Script: Cyrillic in JSON and HTML."""
    report = tmp_path / "rus.html"
    output = tmp_path / "out.json"
    rus_data = '{"результат": "пройдено", "логи": "всё ок"}'
    create_report(report, data=rus_data)

    prog.PytestHtmlJsonExtractor.exec(str(report), True, str(output), True)

    with open(output, "r", encoding="utf-8") as f:
        assert json.load(f)["результат"] == "пройдено"
    return


# ------------------------------------------------------------------------
def test_009__missing_container_tag(tmp_path):
    """Case: There is a tag with an ID, but there is no data in it."""
    report = tmp_path / "empty_tag.html"
    # Создаем отчет, где у дива нет атрибута data-jsonblob
    content = (
        '<html><div id="data-container"></div><a href="pytest-html">v4.0.2</a></html>'
    )
    report.write_text(content, encoding="utf-8")

    with pytest.raises(RuntimeError, match="does not countains json data"):
        prog.PytestHtmlJsonExtractor.exec(str(report), True, "out.json", True)
    return


# ------------------------------------------------------------------------
def test_010__not_an_html_file(tmp_path):
    """Case: Garbage was fed to the input instead of HTML."""
    report = tmp_path / "garbage.html"
    report.write_bytes(os.urandom(1024))  # We write 1 KB of random bytes

    with pytest.raises(UnicodeDecodeError) as x:
        prog.PytestHtmlJsonExtractor.exec(str(report), True, "out.json", True)

    logging.info(
        "Exception ({}): {}".format(
            type(x.value),
            x.value,
        )
    )
    return


# ------------------------------------------------------------------------
def test_011__output_permission_denied(tmp_path):
    """Case: Cannot write to output file."""
    report = tmp_path / "report.html"
    create_report(report)

    output = tmp_path / "readonly.json"
    output.write_text("{}")
    os.chmod(output, 0o444)  # Making a file read-only.

    with pytest.raises(PermissionError):
        prog.PytestHtmlJsonExtractor.exec(str(report), True, str(output), replace=True)
    return


# ------------------------------------------------------------------------
def test_012_multiple_versions_in_text(tmp_path):
    """Case: There are similar lines in the text, but the version is the same."""
    report = tmp_path / "tricky_version.html"
    content = """
    <a href="pytest-html">v4.0.2</a>
    <p>Some other text with v1.0.0 mention</p>
    <div id="data-container" data-jsonblob="{}"></div>
    """
    report.write_text(content, encoding="utf-8")
    # Должен выцепить именно ту, что в ссылке
    prog.PytestHtmlJsonExtractor.exec(str(report), True, "out.json", True)
    return


# //////////////////////////////////////////////////////////////////////////////
