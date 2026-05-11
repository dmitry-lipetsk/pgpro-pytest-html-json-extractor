# /////////////////////////////////////////////////////////////////////////////
import os
import sys
import shutil
import tempfile
import subprocess
import logging
import typing

from pathlib import Path

# /////////////////////////////////////////////////////////////////////////////


class E2EWorkspace:
    def __init__(self, prefix="extractor_e2e_"):
        self.root = Path(tempfile.mkdtemp(prefix=prefix))
        self.reports_dir = self.root / "reports"
        self.reports_dir.mkdir()
        self.src_path = Path(__file__).parent.parent.parent / "src"

    # --------------------------------------------------------------------
    def cleanup(self):
        """We delete everything after ourselves."""
        if self.root.exists():
            shutil.rmtree(self.root)

    # --------------------------------------------------------------------
    def generate_report(
        self,
        name: str,
        test_code: str,
        metadata: typing.Optional[
            typing.Union[typing.Dict[str, typing.Any], str]
        ] = None,
    ) -> str:
        test_file = self.root / f"test_{name}.py"
        test_file.write_text(test_code)

        report_path = self.reports_dir / f"{name}.html"

        # Use sys.executable, to be in our venv
        cmd = [
            sys.executable,
            "-m",
            "pytest",
            f"--html={report_path}",
            "--self-contained-html",
            "-c",
            "/dev/null",
            "-p",
            "no:cacheprovider",  # it disables create ,pytest_cache in /dev
            str(test_file),
        ]

        if metadata is None:
            pass
        elif type(metadata) is str:
            cmd.extend(["--metadata-from-json", metadata])
        elif type(metadata) is dict:
            for k, v in metadata.items():
                cmd.extend(["--metadata", str(k), str(v)])
        else:
            raise RuntimeError(
                "Unsupported metadata type [{}].".format(type(metadata).__name__)
            )

        result = subprocess.run(cmd, capture_output=True, text=True)

        # Code 0 — OK,
        # Code 1 — there are failed tests.
        # Code 5 - no any tests were executed
        if result.returncode not in [0, 1, 5]:
            logging.info(f"STDOUT: {result.stdout}")
            logging.info(f"STDERR: {result.stderr}")
            raise subprocess.CalledProcessError(result.returncode, cmd)

        # CRITICAL CHECK: Verify that the report file was actually created
        if not report_path.exists():
            logging.info(f"STDOUT: {result.stdout}")
            logging.info(f"STDERR: {result.stderr}")
            raise FileNotFoundError(
                f"Pytest finished with code {result.returncode}, "
                f"but failed to generate report at: {report_path}"
            )

        return str(report_path)

    # --------------------------------------------------------------------
    def run_extractor(self, args: list):
        env = os.environ.copy()
        # Add 'src' to PYTHONPATH so python can find the package
        env["PYTHONPATH"] = str(self.src_path)
        cmd = [sys.executable, "-m", "pgpro_pytest_html_json_extractor"] + args
        return subprocess.run(cmd, capture_output=True, text=True, env=env)


# /////////////////////////////////////////////////////////////////////////////
