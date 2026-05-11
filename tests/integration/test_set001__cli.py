import pytest
import subprocess
import os
import typing
import sys
import json
import re

from src.pgpro_pytest_html_json_extractor import __version__ as prog_version

# //////////////////////////////////////////////////////////////////////////////


def run_cli(args: typing.List[str]) -> subprocess.CompletedProcess:
    """
    Helper to run the CLI with correct PYTHONPATH.
    """
    env = os.environ.copy()
    # Add 'src' to PYTHONPATH so python can find the package
    env["PYTHONPATH"] = "src" + os.pathsep + env.get("PYTHONPATH", "")

    return subprocess.run(
        [sys.executable, "-m", "pgpro_pytest_html_json_extractor"] + args,
        capture_output=True,
        text=True,
        env=env,
    )


# //////////////////////////////////////////////////////////////////////////////


def test_cli_001__no_args():
    """
    Test calling the utility without any arguments.
    """
    result = run_cli([])

    # Check for usage info or argparse error
    assert "usage:" in result.stdout.lower() or "error" in result.stderr.lower()
    assert result.returncode in [0, 2]
    return


# ------------------------------------------------------------------------
def test_cli_002__help():
    """
    Test calling the utility with --help.
    It should exit with 0 and show the description.
    """
    # Call with -h
    result = run_cli(["-h"])

    assert result.returncode == 0
    # Check that our keywords are in the output
    output = result.stdout
    assert "usage:" in output
    assert "A tool to extract json data from pytest-html report." in output
    assert "--out" in output
    assert "--no-check-json" in output
    assert "--replace" in output
    assert "--verbose" in output
    return


# ------------------------------------------------------------------------
def test_cli_003__non_existent_file():
    """
    Test calling with a file path that does not exist.
    Should report an error and exit with code 1.
    """
    result = run_cli(
        [
            "non_existent_report.html",
            "-o",
            "result.json",
        ]
    )

    assert result.returncode == 1
    # Check that we collected the error message
    assert "Invalid input" in result.stderr
    assert "non_existent_report.html" in result.stderr
    assert "Termination due to input errors" in result.stderr
    return


# ------------------------------------------------------------------------
@pytest.mark.parametrize(
    "input_file_name",
    [
        "cli_report.html",
        "cli_report.htm",
        "report-123.321.html",
    ],
)
def test_cli_004__full_cycle(tmp_path, input_file_name):
    """
    Full cycle: create HTML -> call CLI -> check JSON.
    """
    # 1. Prepare
    report = tmp_path / input_file_name
    output = tmp_path / "cli_out.json"

    content = """
    <html>
        <div id="data-container" data-jsonblob='{"cli_test": "passed"}'></div>
        <a href="pytest-html">v4.0.2</a>
    </html>
    """
    report.write_text(content, encoding="utf-8")

    # 2. Run: pgpro-... --out output.json report.html
    result = run_cli(["--out", str(output), str(report), "--verbose"])

    # 3. Check status and files
    assert result.returncode == 0
    assert "Successfully extracted json" in str(result.stderr)
    assert "" in str(result.stdout)

    assert output.exists()
    with open(output, "r") as f:
        data = json.load(f)
        assert data["cli_test"] == "passed"
    return


# ------------------------------------------------------------------------
def test_cli_005__replace_logic(tmp_path):
    """
    Checking the rewrite logic via the CLI:
    1. First run - file created.
    2. Second run WITHOUT -r - error.
    3. Third run WITH -r - success.
    """
    report = tmp_path / "report.html"
    output = tmp_path / "out.json"

    # Create minimally valid HTML
    content = '<html><div id="data-container" data-jsonblob="{}"></div><a href="pytest-html">v4.0.2</a></html>'
    report.write_text(content, encoding="utf-8")

    # 1. First pass - OK
    res1 = run_cli(["--out", str(output), str(report)])
    assert res1.returncode == 0
    assert output.exists()

    # 2. Second pass without -r - Should fail (since the file already exists)
    res2 = run_cli(["--out", str(output), str(report)])
    # argparse will work, but the logic for opening the file in mode 'x' will fail
    assert res2.returncode != 0

    # 3. Third pass with -r - OK again
    res3 = run_cli(["--out", str(output), str(report), "--replace", "--verbose"])
    assert res3.returncode == 0
    assert "Successfully extracted" in res3.stderr
    return


# ------------------------------------------------------------------------
def test_cli_006__verbosity_levels(tmp_path):
    """
    Checking that the -v flag affects the output to stderr.
    (With -v or -vv , there should be more logs.)
    """
    report = tmp_path / "report.html"
    output = tmp_path / "out.json"
    content = '<html><div id="data-container" data-jsonblob="{}"></div><a href="pytest-html">v4.0.2</a></html>'
    report.write_text(content, encoding="utf-8")

    # Compare running without -v and with -vv
    res_normal = run_cli(["--out", str(output), str(report), "--replace"])
    res_verbose = run_cli(["--out", str(output), str(report), "--replace", "-vv"])

    # In verbose mode, stderr should be longer due to DEBUG messages.
    # For example, your line "opts = Namespace(...)" will appear there.
    assert len(res_verbose.stderr) > len(res_normal.stderr)
    assert "DEBUG" in res_verbose.stderr or "opts =" in res_verbose.stderr
    return


# ------------------------------------------------------------------------
@pytest.mark.parametrize(
    "input_file",
    [
        ("cli_report", ""),
        ("cli_report.", "."),
        ("cli_report.html2", ".html2"),
        ("cli_report.htm2", ".htm2"),
    ],
)
def test_cli_007__bad_input_file_extension(tmp_path, input_file):
    """
    Bad input file extension.
    """
    # 1. Prepare
    report = tmp_path / input_file[0]
    output = tmp_path / "cli_out.json"

    content = """
    <html>
        <div id="data-container" data-jsonblob='{"cli_test": "passed"}'></div>
        <a href="pytest-html">v4.0.2</a>
    </html>
    """
    report.write_text(content, encoding="utf-8")

    # 2. Run: pgpro-... --out output.json report.html
    result = run_cli(["--out", str(output), str(report), "--verbose"])

    # 3. Check status
    assert result.returncode == 2

    assert "Bad input file extension: '{}'. It was expecting one from ['.html', '.htm'].".format(
        input_file[1],
    ) in str(
        result.stderr
    )
    assert "" in str(result.stdout)
    return


# ------------------------------------------------------------------------
@pytest.mark.parametrize(
    "output_file",
    [
        ("cli_out", ""),
        ("cli_out.", "."),
        ("cli_out.jso", ".jso"),
        ("cli_out.json2", ".json2"),
    ],
)
def test_cli_008__bad_output_file_extension(tmp_path, output_file):
    """
    Bad input file extension.
    """
    # 1. Prepare
    report = tmp_path / "cli_input.html"
    output = tmp_path / output_file[0]

    content = """
    <html>
        <div id="data-container" data-jsonblob='{"cli_test": "passed"}'></div>
        <a href="pytest-html">v4.0.2</a>
    </html>
    """
    report.write_text(content, encoding="utf-8")

    # 2. Run: pgpro-... --out output.json report.html
    result = run_cli(["--out", str(output), str(report), "--verbose"])

    # 3. Check status
    assert result.returncode == 2

    assert (
        "Bad output file extension: '{}'. It was expecting one from ['.json'].".format(
            output_file[1],
        )
        in str(result.stderr)
    )
    assert "" in str(result.stdout)
    return


# ------------------------------------------------------------------------
def test_cli_009__version():
    """
    Check that --version prints the version and exits with code 0.
    """
    result = run_cli(["--version"])

    assert result.returncode == 0
    # We check that the output contains the version of our utility.
    assert re.search(re.escape(" " + prog_version) + "$", result.stdout) is not None
    return


# //////////////////////////////////////////////////////////////////////////////
