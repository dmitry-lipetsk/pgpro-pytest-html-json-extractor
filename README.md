[![CI Status](https://img.shields.io/github/actions/workflow/status/postgrespro/pgpro-pytest-html-json-extractor/.github/workflows/ci.yml?label=CI)](https://github.com/postgrespro/pgpro-pytest-html-json-extractor/actions/workflows/ci.yml)
[![PyPI package version](https://badge.fury.io/py/pgpro-pytest-html-json-extractor.svg)](https://badge.fury.io/py/pgpro-pytest-html-json-extractor)
[![PyPI python versions](https://img.shields.io/pypi/pyversions/pgpro-pytest-html-json-extractor)](https://pypi.org/project/pgpro-pytest-html-json-extractor)

# pgpro-pytest-html-json-extractor
A tool to extract json data from pytest-html report. Developed and maintained by Postgres Professional.

## Key features
- Extractor supports pytest-html v4.0.2+
- Extractor produces JSON with unescaped HTML entities in log messages (for pytest-html v4.1.0+)

## Installation
You can install the package directly from the repository (until it's published to PyPI):
```bash
pip install pgpro-pytest-html-json-extractor
```

## Usage

After installation, the tool is available via the pgpro-pytest-html-json-extractor command.

### Basic Examples
Extract JSON from a report:
```bash
pgpro-pytest-html-json-extractor report.html -o report.json
```

### Command Line Arguments

| Argument | Shorthand | Required | Description | Default |
| :--- | :--- | :--- | :--- | :--- |
| `--version` | | No | Show program's version number and exit | None |
| `--out` | `-o` | Yes | Name of the output JSON file | None |
| `--verbose` | `-v` | No | Level of logging verbosity | 3 |
| `--no-check-json` | | No | Do not validate json data after extraction | None |
| `--no-unescape-logs` | | No | Do not unescape HTML entities in logs | None |
| `--replace` | `-r` | No | Replace output if it exists | None |
| `input` | | Yes | Positional argument for HTML file | None |

## Contributing
1. Fork the repository.
2. Create your feature branch (`git checkout -b feature/amazing-feature`).
3. Commit your changes (`git commit -m 'feat: add some amazing feature'`).
4. Push to the branch (`git push origin feature/amazing-feature`).
5. Open a Pull Request.

## License
This project is licensed under the MIT License - see the LICENSE file for details.

© 2026 Postgres Professional
