# //////////////////////////////////////////////////////////////////////////////
import json
import logging

from .e2eworkspace import E2EWorkspace
from importlib.metadata import version as get_package_version

# //////////////////////////////////////////////////////////////////////////////


def test_e2e_001__single_report_metadata():
    """
    E2E Test: Generate one report with specific metadata and merge it.
    Verifies that metadata and basic structure are preserved.
    """
    ws = E2EWorkspace(prefix="e2e_single_")
    try:
        # 1. Generate a single report with metadata
        # We use a simple test that definitely passes
        test_code = "def test_logic(): assert 2 + 2 == 4"
        metadata = {"Project": "Alpha-Centauri", "User": "Tester-Dima"}

        html = ws.generate_report("run1", test_code, metadata=metadata)

        # 2. Define output path and run merger
        output_json = ws.root / "output_json.json"
        # We point to the directory where run1.html was generated
        result = ws.run_extractor(
            [
                str(html),
                "-o",
                str(output_json),
            ]
        )

        # 3. Assertions
        assert result.returncode == 0, f"Merger failed: {result.stderr}"
        assert output_json.exists(), "Output JSON file was not created."

        content = output_json.read_text()

        assert content is not None
        assert content != ""

        data = json.loads(content)

        # Checking Environment Metadata
        env = data.get("environment")
        assert env is not None
        assert env.get("Project") == "Alpha-Centauri", "Wrong Project: {}".format(
            env.get("Project")
        )

        # We check that the pytest-html version in JSON matches the actual version.
        plugins = env.get("Plugins")
        assert plugins is not None
        assert "html" in plugins, "pytest-html version missing in environment"

        expected_html_version = get_package_version("pytest-html")
        logging.info("expected_html_version: {}".format(expected_html_version))

        actual_html_version = plugins.get("html")
        assert actual_html_version is not None
        assert actual_html_version == expected_html_version

        # Checking the test results
        tests = data.get("tests", {})
        # The key usually contains a path, we are looking for the ending ::test_logic
        test_entry = next((v for k, v in tests.items() if "test_logic" in k), None)

        assert test_entry is not None, "Test 'test_logic' not found in JSON"
        assert (
            test_entry[0]["result"] == "Passed"
        ), f"Expected Passed, got {test_entry[0]['result']}"

        # Checking the report title
        assert data.get("title") == "run1.html"

        logging.info("E2E data validation passed successfully!")
    finally:
        pass

    ws.cleanup()
    return


# //////////////////////////////////////////////////////////////////////////////
