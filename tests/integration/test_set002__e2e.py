# //////////////////////////////////////////////////////////////////////////////
import pytest
import json
import logging
import dataclasses
import typing
import pytest_html

from .e2eworkspace import E2EWorkspace
from ..helpers import test_spec

from importlib.metadata import version as get_package_version
from packaging.version import Version

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

        # 2. Define output path and run extractor
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
        assert result.returncode == 0, f"Extractor failed: {result.stderr}"
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


# ------------------------------------------------------------------------
@dataclasses.dataclass
class tagData002:
    test_spec: typing.Optional[str]
    data: str
    in_html: str
    in_json: str
    sign: str


# ------------------------------------------------------------------------
g_Data002__html4_0_2: typing.List[tagData002] = [
    tagData002(
        test_spec=None,
        data="text",
        in_html="text",
        in_json="text",
        sign="text",
    ),
    tagData002(
        test_spec="PYTEST_HTML<'4.1.0'",
        data='"text"',
        in_html="\\&#34;text\\&#34;",
        in_json='\\"text\\"',
        sign="quoted_text__pytest_html4_0_2",
    ),
    # Mark G. ------------------------------------------------------------
    # Case 1: Classic quotation marks (already tested, but let's keep it for now)
    tagData002(
        test_spec="PYTEST_HTML<'4.1.0'",
        data='{"msg": "simple quote"}',
        in_html="{\\&#34;msg\\&#34;: \\&#34;simple quote\\&#34;}",
        in_json='{\\"msg\\": \\"simple quote\\"}',
        sign="simple_quote__pytest_html4_0_2",
    ),
    # Case 2: That same "double" ampersand from the pytest-html logs
    tagData002(
        test_spec="PYTEST_HTML<'4.1.0'",
        data="Double &amp;quot;nested&amp;quot; test",
        in_html="Double &amp;amp;quot;nested&amp;amp;quot;",
        in_json="Double &amp;quot;nested&amp;quot; test",
        sign="double_nested_quotes__pytest_html4_0_2",
    ),
    # Case 3: HTML tags that frequently appear in test results (e.g., browser output)
    tagData002(
        test_spec="PYTEST_HTML<'4.1.0'",
        data='<div class="test">Data</div>',
        in_html="&lt;div class=\\&#34;test\\&#34;&gt;Data&lt;/div&gt;",
        in_json='<div class=\\"test\\">Data</div>',
        sign="html_tags_in_log__pytest_html4_0_2",
    ),
    # Case 4: Different Entities in a Single String (Unescaping Greediness Check)
    tagData002(
        test_spec="PYTEST_HTML<'4.1.0'",
        data="Check: & &lt; &gt; \" '",
        in_html="Check: &amp; &amp;lt; &amp;gt; \\&#34; &#39;",
        in_json="Check: & &lt; &gt; \\\" '",
        sign="mixed_entities__pytest_html4_0_2",
    ),
    # Case 5: Backslashes (to avoid breaking JSON escaping)
    tagData002(
        test_spec=None,
        data=r"Path C:\Users\Dima",
        in_html=r"Path C:\\Users\\Dima",
        in_json=r"Path C:\\Users\\Dima",  # JSON must double slashes
        sign="backslash_test",
    ),
    # --------------------------------------------------------------------
    tagData002(
        test_spec="PYTEST_HTML<'4.1.0'",
        data="<b>text<b>",
        in_html="&lt;b&gt;text&lt;b&gt;",
        in_json="<b>text<b>",
        sign="html_with_bold_text__pytest_html4_0_2",
    ),
    tagData002(
        test_spec="PYTEST_HTML<'4.1.0'",
        data='<span style="font-weight: bold; color: red; font-size: 2em;">text</span>',
        in_html="&lt;span style=\\&#34;font-weight: bold; color: red; font-size: 2em;\\&#34;&gt;text&lt;/span&gt;",
        in_json='<span style=\\"font-weight: bold; color: red; font-size: 2em;\\">text</span>',
        sign="html_with_bold_red_LARGE_text__pytest_html4_0_2",
    ),
]


# ------------------------------------------------------------------------
g_Data002__html4_1_0: typing.List[tagData002] = [
    tagData002(
        test_spec=None,
        data="text",
        in_html="text",
        in_json="text",
        sign="text",
    ),
    tagData002(
        test_spec="PYTEST_HTML>='4.1.0'",
        data='"text"',
        in_html="&amp;quot;text&amp;quot;",
        in_json='\\"text\\"',
        sign="quoted_text",
    ),
    # Mark G. ------------------------------------------------------------
    # Case 1: Classic quotation marks (already tested, but let's keep it for now)
    tagData002(
        test_spec="PYTEST_HTML>='4.1.0'",
        data='{"msg": "simple quote"}',
        in_html="{&amp;quot;msg&amp;quot;: &amp;quot;simple quote&amp;quot;}",
        in_json='{\\"msg\\": \\"simple quote\\"}',
        sign="simple_quote",
    ),
    # Case 2: That same "double" ampersand from the pytest-html logs
    tagData002(
        test_spec="PYTEST_HTML>='4.1.0'",
        data="Double &amp;quot;nested&amp;quot; test",
        in_html="Double &amp;amp;amp;quot;nested&amp;amp;amp;quot;",
        in_json="Double &amp;quot;nested&amp;quot; test",
        sign="double_nested_quotes",
    ),
    # Case 3: HTML tags that frequently appear in test results (e.g., browser output)
    tagData002(
        test_spec="PYTEST_HTML>='4.1.0'",
        data='<div class="test">Data</div>',
        in_html="&amp;lt;div class=&amp;quot;test&amp;quot;&amp;gt;Data&amp;lt;/div&amp;gt;",
        in_json='<div class=\\"test\\">Data</div>',
        sign="html_tags_in_log",
    ),
    # Case 4: Different Entities in a Single String (Unescaping Greediness Check)
    tagData002(
        test_spec="PYTEST_HTML>='4.1.0'",
        data="Check: & &lt; &gt; \" '",
        in_html="Check: &amp;amp; &amp;amp;lt; &amp;amp;gt; &amp;quot; &amp;#x27;",
        in_json="Check: & &lt; &gt; \\\" '",
        sign="mixed_entities",
    ),
    # Case 5: Backslashes (to avoid breaking JSON escaping)
    tagData002(
        test_spec=None,
        data=r"Path C:\Users\Dima",
        in_html=r"Path C:\\Users\\Dima",
        in_json=r"Path C:\\Users\\Dima",  # JSON must double slashes
        sign="backslash_test",
    ),
    # --------------------------------------------------------------------
    tagData002(
        test_spec="PYTEST_HTML>='4.1.0'",
        data="<b>text<b>",
        in_html="&amp;lt;b&amp;gt;text&amp;lt;b&amp;gt;",
        in_json="<b>text<b>",
        sign="html_with_bold_text",
    ),
    tagData002(
        test_spec="PYTEST_HTML>='4.1.0'",
        data='<span style="font-weight: bold; color: red; font-size: 2em;">text</span>',
        in_html="&amp;lt;span style=&amp;quot;font-weight: bold; color: red; font-size: 2em;&amp;quot;&amp;gt;text&amp;lt;/span&amp;gt;",
        in_json='<span style=\\"font-weight: bold; color: red; font-size: 2em;\\">text</span>',
        sign="html_with_bold_red_LARGE_text",
    ),
]


# ------------------------------------------------------------------------
def Data002Selector() -> typing.List[tagData002]:
    html_ver = Version(pytest_html.__version__)

    if html_ver < Version("4.1.0"):
        return g_Data002__html4_0_2

    return g_Data002__html4_1_0


# ------------------------------------------------------------------------
@pytest.fixture(params=[pytest.param(x, id=x.sign) for x in Data002Selector()])
def data002(request: pytest.FixtureRequest) -> tagData002:
    assert isinstance(request, pytest.FixtureRequest)
    assert type(request.param) is tagData002
    return request.param


# ------------------------------------------------------------------------
def test_e2e_002__unescape_logs__DEFAULT(data002: tagData002):
    _test_e2e_002__unescape_logs(
        data002,
        False,
    )


# ------------------------------------------------------------------------
def test_e2e_002__unescape_logs__AUTO(data002: tagData002):
    _test_e2e_002__unescape_logs(
        data002,
        True,
    )


# ------------------------------------------------------------------------
def _test_e2e_002__unescape_logs(
    data002: tagData002,
    explicit_auto: bool,
):
    """
    E2E Test: Generate one report quote output.
    Verifies that json does not has "&quot;".
    """
    assert type(data002) is tagData002
    assert type(explicit_auto) is bool

    assert test_spec.TestSpec.can_run(data002.test_spec)

    ws = E2EWorkspace(prefix="e2e_unescape_")
    try:
        # 1. Generate a single report with metadata
        # We use a simple test that definitely passes
        test_code = "def test_unescape(): print({})".format(
            repr(data002.data),
        )

        html = ws.generate_report("run1", test_code)

        with open(html, "r", encoding="utf-8") as f:
            html_content = f.read()

        assert data002.in_html in html_content

        # 2. Define output path and run extractor
        output_json = ws.root / "output_json.json"
        # We point to the directory where run1.html was generated
        cmd = [
            str(html),
            "-o",
            str(output_json),
        ]

        if explicit_auto:
            cmd += [
                "--unescape-logs",
                "auto",
            ]

        result = ws.run_extractor(cmd)

        # 3. Assertions
        assert result.returncode == 0, f"Extractor failed: {result.stderr}"
        assert output_json.exists(), "Output JSON file was not created."

        json_content = output_json.read_text()

        assert json_content is not None
        assert json_content != ""
        assert data002.in_json in json_content

        data = json.loads(json_content)
        assert data is not None

        data1 = next(iter(data["tests"].values()))
        assert type(data1) is list
        data2 = next(iter(data1))
        assert type(data2) is dict
        log = data2["log"]
        assert data002.data in log

        logging.info("All is OK!")
    finally:
        pass

    ws.cleanup()
    return


# ------------------------------------------------------------------------
@dataclasses.dataclass
class tagData003:
    test_spec: typing.Optional[str]
    data: str
    in_html: str
    in_json: str
    in_testID: str
    sign: str


# ------------------------------------------------------------------------
g_Data003: typing.List[tagData003] = [
    tagData003(
        test_spec=None,
        data="text",
        in_html="text",
        in_json="text",
        in_testID="text",
        sign="text",
    ),
    tagData003(
        test_spec=None,
        data='"text"',
        in_html="\\&#34;text\\&#34;",
        in_json='\\"text\\"',
        in_testID='"text"',
        sign="quoted_text",
    ),
    # Mark G. ------------------------------------------------------------
    tagData003(
        test_spec=None,
        data='{"msg": "simple quote"}',
        in_html="{\\&#34;msg\\&#34;: \\&#34;simple quote\\&#34;}",
        in_json='{\\"msg\\": \\"simple quote\\"}',
        in_testID='{"msg": "simple quote"}',
        sign="simple_quote",
    ),
    tagData003(
        test_spec=None,
        data="Double &amp;quot;nested&amp;quot; test",
        in_html="Double &amp;amp;quot;nested&amp;amp;quot; test",
        in_json="Double &amp;quot;nested&amp;quot; test",
        in_testID="Double &amp;quot;nested&amp;quot; test",
        sign="double_nested_quotes",
    ),
    tagData003(
        test_spec=None,
        data='<div class="test">Data</div>',
        in_html="&lt;div class=\\&#34;test\\&#34;&gt;Data&lt;/div&gt;",
        in_json='<div class=\\"test\\">Data</div>',
        in_testID='<div class="test">Data</div>',
        sign="html_tags_in_log",
    ),
    # Case 4: Different entities in one line
    tagData003(
        test_spec=None,
        data="Check: & &lt; &gt; \" '",
        in_html="Check: &amp; &amp;lt; &amp;gt; \\&#34; &#39;",
        in_json="Check: & &lt; &gt; \\\" '",
        in_testID="Check: & &lt; &gt; \" '",
        sign="mixed_entities",
    ),
    # Case 5: Backslashes (to avoid breaking JSON escaping)
    tagData003(
        test_spec=None,
        data="Path C:\\Users\\Dima",  # <------- ONE!
        in_html=r"Path C:\\\\Users\\\\Dima",  # <------- FOUR!!!
        in_json=r"Path C:\\\\Users\\\\Dima",  # <------- FOUR!!!
        in_testID="Path C:\\\\Users\\\\Dima",  # <------- TWO!!!
        sign="backslash_test - Path C:\\Users\\Dima",
    ),
    # --------------------------------------------------------------------
    tagData003(
        test_spec=None,
        data="<b>text<b>",
        in_html="&lt;b&gt;text&lt;b&gt;",
        in_json="<b>text<b>",
        in_testID="<b>text<b>",
        sign="html_with_bold_text",
    ),
    tagData003(
        test_spec=None,
        data='<span style="font-weight: bold; color: red; font-size: 2em;">text</span>',
        in_html="&lt;span style=\\&#34;font-weight: bold; color: red; font-size: 2em;\\&#34;&gt;text&lt;/span&gt;",
        in_json='<span style=\\"font-weight: bold; color: red; font-size: 2em;\\">text</span>',
        in_testID='<span style="font-weight: bold; color: red; font-size: 2em;">text</span>',
        sign="html_with_bold_red_LARGE_text",
    ),
]


# ------------------------------------------------------------------------
@pytest.fixture(params=g_Data003, ids=[x.sign for x in g_Data003])
def data003(request: pytest.FixtureRequest) -> tagData003:
    assert isinstance(request, pytest.FixtureRequest)
    assert type(request.param) is tagData003
    return request.param


# ------------------------------------------------------------------------
def test_e2e_003__unescape_html_in_testId(request, data003: tagData003):
    """
    E2E Test: Generate one report quote output.
    Verifies that json does not has "&quot;".
    """
    assert isinstance(request, pytest.FixtureRequest)
    assert type(data003) is tagData003

    assert test_spec.TestSpec.can_run(data003.test_spec)

    ws = E2EWorkspace(prefix="e2e_unescape_")
    try:
        # 1. Generate a single report with metadata
        # We use a simple test that definitely passes
        test_code = """
import pytest
@pytest.mark.parametrize(
    "data",
    [
        {},
    ],
)
def test_unescape(data): print("ha-ha")
""".format(
            repr(data003.data),
        )

        html = ws.generate_report("run1", test_code)

        with open(html, "r", encoding="utf-8") as f:
            html_content = f.read()

        assert data003.in_html in html_content

        # 2. Define output path and run extractor
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
        assert result.returncode == 0, f"Extractor failed: {result.stderr}"
        assert output_json.exists(), "Output JSON file was not created."

        json_content = output_json.read_text()

        assert json_content is not None
        assert json_content != ""
        assert data003.in_json in json_content

        data = json.loads(json_content)
        assert data is not None

        data1 = next(iter(data["tests"].values()))
        assert type(data1) is list
        data2 = next(iter(data1))
        assert type(data2) is dict
        testId = data2["testId"]
        assert data003.in_testID in testId

        logging.info("All is OK!")
    finally:
        pass

    ws.cleanup()
    return


# ------------------------------------------------------------------------
@dataclasses.dataclass
class tagData004:
    test_spec: typing.Optional[str]
    data: str
    in_html: str
    in_json: str
    in_log: str
    sign: str


# ------------------------------------------------------------------------
g_Data004__html4_0_2: typing.List[tagData004] = [
    tagData004(
        test_spec=None,
        data="text",
        in_html="text",
        in_json="text",
        in_log="text",
        sign="text",
    ),
    tagData004(
        test_spec="PYTEST_HTML<'4.1.0'",
        data='"text"',
        in_html="\\&#34;text\\&#34;",
        in_json='\\"text\\"',
        in_log='"text"',
        sign="quoted_text__pytest_html4_0_2",
    ),
    # Mark G. ------------------------------------------------------------
    tagData004(
        test_spec="PYTEST_HTML<'4.1.0'",
        data='{"msg": "simple quote"}',
        in_html="{\\&#34;msg\\&#34;: \\&#34;simple quote\\&#34;}",
        in_json='{\\"msg\\": \\"simple quote\\"}',
        in_log='{"msg": "simple quote"}',
        sign="simple_quote__pytest_html4_0_2",
    ),
    tagData004(
        test_spec="PYTEST_HTML<'4.1.0'",
        data="Double &amp;quot;nested&amp;quot; test",
        in_html="Double &amp;amp;quot;nested&amp;amp;quot;",
        in_json="Double &amp;quot;nested&amp;quot; test",
        in_log="Double &amp;quot;nested&amp;quot; test",
        sign="double_nested_quotes__pytest_html4_0_2",
    ),
    tagData004(
        test_spec="PYTEST_HTML<'4.1.0'",
        data='<div class="test">Data</div>',
        in_html="&lt;div class=\\&#34;test\\&#34;&gt;Data&lt;/div&gt;",
        in_json='<div class=\\"test\\">Data</div>',
        in_log='<div class="test">Data</div>',
        sign="html_tags_in_log__pytest_html4_0_2",
    ),
    tagData004(
        test_spec="PYTEST_HTML<'4.1.0'",
        data="Check: & &lt; &gt; \" '",
        in_html="Check: &amp; &amp;lt; &amp;gt; \\&#34; &#39;",
        in_json="Check: & &lt; &gt; \\\" '",
        in_log="Check: & &lt; &gt; \" '",
        sign="mixed_entities__pytest_html4_0_2",
    ),
    tagData004(
        test_spec=None,
        data=r"Path C:\Users\Dima",
        in_html=r"Path C:\\Users\\Dima",
        in_json=r"Path C:\\Users\\Dima",
        in_log="",
        sign="backslash_test",
    ),
    # --------------------------------------------------------------------
    tagData004(
        test_spec="PYTEST_HTML<'4.1.0'",
        data="<b>text<b>",
        in_html="&lt;b&gt;text&lt;b&gt;",
        in_json="<b>text<b>",
        in_log="<b>text<b>",
        sign="html_with_bold_text__pytest_html4_0_2",
    ),
    tagData004(
        test_spec="PYTEST_HTML<'4.1.0'",
        data='<span style="font-weight: bold; color: red; font-size: 2em;">text</span>',
        in_html="&lt;span style=\\&#34;font-weight: bold; color: red; font-size: 2em;\\&#34;&gt;text&lt;/span&gt;",
        in_json='<span style=\\"font-weight: bold; color: red; font-size: 2em;\\">text</span>',
        in_log='<span style="font-weight: bold; color: red; font-size: 2em;">text</span>',
        sign="html_with_bold_red_LARGE_text__pytest_html4_0_2",
    ),
]

# ------------------------------------------------------------------------
g_Data004__html4_1_0: typing.List[tagData004] = [
    tagData004(
        test_spec=None,
        data="text",
        in_html="text",
        in_json="text",
        in_log="text",
        sign="text",
    ),
    tagData004(
        test_spec="PYTEST_HTML>='4.1.0'",
        data='"text"',
        in_html="&amp;quot;text&amp;quot;",
        in_json="&quot;text&quot;",
        in_log="&quot;text&quot;",
        sign="quoted_text",
    ),
    # Mark G. ------------------------------------------------------------
    tagData004(
        test_spec="PYTEST_HTML>='4.1.0'",
        data='{"msg": "simple quote"}',
        in_html="{&amp;quot;msg&amp;quot;: &amp;quot;simple quote&amp;quot;}",
        in_json="{&quot;msg&quot;: &quot;simple quote&quot;}",
        in_log="{&quot;msg&quot;: &quot;simple quote&quot;}",
        sign="simple_quote",
    ),
    tagData004(
        test_spec="PYTEST_HTML>='4.1.0'",
        data="Double &amp;quot;nested&amp;quot; test",
        in_html="Double &amp;amp;amp;quot;nested&amp;amp;amp;quot;",
        in_json="Double &amp;amp;quot;nested&amp;amp;quot; test",
        in_log="Double &amp;amp;quot;nested&amp;amp;quot; test",
        sign="double_nested_quotes",
    ),
    tagData004(
        test_spec="PYTEST_HTML>='4.1.0'",
        data='<div class="test">Data</div>',
        in_html="&amp;lt;div class=&amp;quot;test&amp;quot;&amp;gt;Data&amp;lt;/div&amp;gt;",
        in_json="&lt;div class=&quot;test&quot;&gt;Data&lt;/div&gt;",
        in_log="&lt;div class=&quot;test&quot;&gt;Data&lt;/div&gt;",
        sign="html_tags_in_log",
    ),
    tagData004(
        test_spec="PYTEST_HTML>='4.1.0'",
        data="Check: & &lt; &gt; \" '",
        in_html="Check: &amp;amp; &amp;amp;lt; &amp;amp;gt; &amp;quot; &amp;#x27;",
        in_json="Check: &amp; &amp;lt; &amp;gt; &quot; &#x27;",
        in_log="Check: &amp; &amp;lt; &amp;gt; &quot; &#x27;",
        sign="mixed_entities",
    ),
    tagData004(
        test_spec=None,
        data=r"Path C:\Users\Dima",
        in_html=r"Path C:\\Users\\Dima",
        in_json=r"Path C:\\Users\\Dima",
        in_log="",
        sign="backslash_test",
    ),
    # --------------------------------------------------------------------
    tagData004(
        test_spec="PYTEST_HTML>='4.1.0'",
        data="<b>text<b>",
        in_html="&amp;lt;b&amp;gt;text&amp;lt;b&amp;gt;",
        in_json="&lt;b&gt;text&lt;b&gt;",
        in_log="&lt;b&gt;text&lt;b&gt;",
        sign="html_with_bold_text",
    ),
    tagData004(
        test_spec="PYTEST_HTML>='4.1.0'",
        data='<span style="font-weight: bold; color: red; font-size: 2em;">text</span>',
        in_html="&amp;lt;span style=&amp;quot;font-weight: bold; color: red; font-size: 2em;&amp;quot;&amp;gt;text&amp;lt;/span&amp;gt;",
        in_json="&lt;span style=&quot;font-weight: bold; color: red; font-size: 2em;&quot;&gt;text&lt;/span&gt;",
        in_log="&lt;span style=&quot;font-weight: bold; color: red; font-size: 2em;&quot;&gt;text&lt;/span&gt;",
        sign="html_with_bold_red_LARGE_text",
    ),
]


# ------------------------------------------------------------------------
def Data004Selector() -> typing.List[tagData004]:
    html_ver = Version(pytest_html.__version__)

    if html_ver < Version("4.1.0"):
        return g_Data004__html4_0_2

    return g_Data004__html4_1_0


# ------------------------------------------------------------------------
@pytest.fixture(params=[pytest.param(x, id=x.sign) for x in Data004Selector()])
def data004(request: pytest.FixtureRequest) -> tagData004:
    assert isinstance(request, pytest.FixtureRequest)
    assert type(request.param) is tagData004
    return request.param


# ------------------------------------------------------------------------
def test_e2e_004__unescape_logs__NO(data004: tagData004):
    """
    E2E Test: Generate one report quote output.
    Verifies that extractor does not touch log.
    """
    assert type(data004) is tagData004

    assert test_spec.TestSpec.can_run(data004.test_spec)

    ws = E2EWorkspace(prefix="e2e_unescape_")
    try:
        # 1. Generate a single report with metadata
        # We use a simple test that definitely passes
        test_code = "def test_unescape(): print({})".format(
            repr(data004.data),
        )

        html = ws.generate_report("run1", test_code)

        with open(html, "r", encoding="utf-8") as f:
            html_content = f.read()

        assert data004.in_html in html_content

        # 2. Define output path and run extractor
        output_json = ws.root / "output_json.json"
        # We point to the directory where run1.html was generated
        result = ws.run_extractor(
            [
                str(html),
                "-o",
                str(output_json),
                "--unescape-logs",
                "no",
            ]
        )

        # 3. Assertions
        assert result.returncode == 0, f"Extractor failed: {result.stderr}"
        assert output_json.exists(), "Output JSON file was not created."

        json_content = output_json.read_text()

        assert json_content is not None
        assert json_content != ""
        assert data004.in_json in json_content

        data = json.loads(json_content)
        assert data is not None

        data1 = next(iter(data["tests"].values()))
        assert type(data1) is list
        data2 = next(iter(data1))
        assert type(data2) is dict
        log = data2["log"]
        assert data004.in_log in log

        logging.info("All is OK!")
    finally:
        pass

    ws.cleanup()
    return


# //////////////////////////////////////////////////////////////////////////////
