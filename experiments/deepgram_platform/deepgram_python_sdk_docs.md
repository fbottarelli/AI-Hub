(Files content cropped to 300k characters, download full ingest to see more)
================================================
File: README.md
================================================
# Deepgram Python SDK

[![Discord](https://dcbadge.vercel.app/api/server/xWRaCDBtW4?style=flat)](https://discord.gg/xWRaCDBtW4) [![GitHub Workflow Status](https://img.shields.io/github/workflow/status/deepgram/deepgram-python-sdk/CI)](https://github.com/deepgram/deepgram-python-sdk/actions/workflows/CI.yml) [![PyPI](https://img.shields.io/pypi/v/deepgram-sdk)](https://pypi.org/project/deepgram-sdk/)
[![Contributor Covenant](https://img.shields.io/badge/Contributor%20Covenant-v2.0%20adopted-ff69b4.svg?style=flat-rounded)](./.github/CODE_OF_CONDUCT.md)

Official Python SDK for [Deepgram](https://www.deepgram.com/). Power your apps with world-class speech and Language AI models.

- [Deepgram Python SDK](#deepgram-python-sdk)
- [Documentation](#documentation)
- [Getting an API Key](#getting-an-api-key)
- [Requirements](#requirements)
- [Installation](#installation)
- [Quickstarts](#quickstarts)
  - [PreRecorded Audio Transcription Quickstart](#prerecorded-audio-transcription-quickstart)
  - [Live Audio Transcription Quickstart](#live-audio-transcription-quickstart)
- [Examples](#examples)
- [Logging](#logging)
- [Backwards Compatibility](#backwards-compatibility)
- [Development and Contributing](#development-and-contributing)
- [Getting Help](#getting-help)

## Documentation

You can learn more about the Deepgram API at [developers.deepgram.com](https://developers.deepgram.com/docs).

## Getting an API Key

🔑 To access the Deepgram API you will need a [free Deepgram API Key](https://console.deepgram.com/signup?jump=keys).

## Requirements

[Python](https://www.python.org/downloads/) (version ^3.10)

## Installation

To install the latest version available (which will guarantee change over time):

```sh
pip install deepgram-sdk
```

If you are going to write an application to consume this SDK, it's [highly recommended](https://discuss.python.org/t/how-to-pin-a-package-to-a-specific-major-version-or-lower/17077) and a [programming staple](https://www.easypost.com/dependency-pinning-guide) to pin to at **least** a major version of an SDK (ie `==2.*`) or **with due diligence**, to a minor and/or specific version (ie `==2.1.*` or `==2.12.0`, respectively). If you are unfamiliar with [semantic versioning or semver](https://semver.org/), it's a must-read.

In a `requirements.txt` file, pinning to a major (or minor) version, like if you want to stick to using the SDK `v2.12.0` release, that can be done like this:

```sh
deepgram-sdk==2.*
```

Or using pip:

```sh
pip install deepgram-sdk==2.*
```

Pinning to a specific version can be done like this in a `requirements.txt` file:

```sh
deepgram-sdk==2.12.0
```

Or using pip:

```sh
pip install deepgram-sdk==2.12.0
```

We guarantee that major interfaces will not break in a given major semver (ie `2.*` release). However, all bets are off moving from a `2.*` to `3.*` major release. This follows standard semver best-practices.

## Quickstarts

This SDK aims to reduce complexity and abtract/hide some internal Deepgram details that clients shouldn't need to know about.  However you can still tweak options and settings if you need.

### PreRecorded Audio Transcription Quickstart

You can find a [walkthrough](https://developers.deepgram.com/docs/python-sdk-pre-recorded-transcription) on our documentation site. Transcribing Pre-Recorded Audio can be done using the following sample code:

```python
AUDIO_URL = {
    "url": "https://static.deepgram.com/examples/Bueller-Life-moves-pretty-fast.wav"
}

## STEP 1 Create a Deepgram client using the API key from environment variables
deepgram: DeepgramClient = DeepgramClient("", ClientOptionsFromEnv())

## STEP 2 Call the transcribe_url method on the prerecorded class
options: PrerecordedOptions = PrerecordedOptions(
    model="nova-3",
    smart_format=True,
)
response = deepgram.listen.rest.v("1").transcribe_url(AUDIO_URL, options)
print(f"response: {response}\n\n")
```

### Live Audio Transcription Quickstart

You can find a [walkthrough](https://developers.deepgram.com/docs/python-sdk-streaming-transcription) on our documentation site. Transcribing Live Audio can be done using the following sample code:

```python
deepgram: DeepgramClient = DeepgramClient()

dg_connection = deepgram.listen.websocket.v("1")

def on_open(self, open, **kwargs):
    print(f"\n\n{open}\n\n")

def on_message(self, result, **kwargs):
    sentence = result.channel.alternatives[0].transcript
    if len(sentence) == 0:
        return
    print(f"speaker: {sentence}")

def on_metadata(self, metadata, **kwargs):
    print(f"\n\n{metadata}\n\n")

def on_speech_started(self, speech_started, **kwargs):
    print(f"\n\n{speech_started}\n\n")

def on_utterance_end(self, utterance_end, **kwargs):
    print(f"\n\n{utterance_end}\n\n")

def on_error(self, error, **kwargs):
    print(f"\n\n{error}\n\n")

def on_close(self, close, **kwargs):
    print(f"\n\n{close}\n\n")

dg_connection.on(LiveTranscriptionEvents.Open, on_open)
dg_connection.on(LiveTranscriptionEvents.Transcript, on_message)
dg_connection.on(LiveTranscriptionEvents.Metadata, on_metadata)
dg_connection.on(LiveTranscriptionEvents.SpeechStarted, on_speech_started)
dg_connection.on(LiveTranscriptionEvents.UtteranceEnd, on_utterance_end)
dg_connection.on(LiveTranscriptionEvents.Error, on_error)
dg_connection.on(LiveTranscriptionEvents.Close, on_close)

options: LiveOptions = LiveOptions(
    model="nova-3",
    punctuate=True,
    language="en-US",
    encoding="linear16",
    channels=1,
    sample_rate=16000,
    ## To get UtteranceEnd, the following must be set:
    interim_results=True,
    utterance_end_ms="1000",
    vad_events=True,
)
dg_connection.start(options)

## create microphone
microphone = Microphone(dg_connection.send)

## start microphone
microphone.start()

## wait until finished
input("Press Enter to stop recording...\n\n")

## Wait for the microphone to close
microphone.finish()

## Indicate that we've finished
dg_connection.finish()

print("Finished")
```

## Examples

There are examples for **every** API call in this SDK. You can find all of these examples in the [examples folder](https://github.com/deepgram/deepgram-python-sdk/tree/main/examples) at the root of this repo.

Before running any of these examples, then you need to take a look at the README and install the following dependencies:

```bash
pip install -r examples/requirements-examples.txt
```

To run each example set the `DEEPGRAM_API_KEY` as an environment variable, then `cd` into each example folder and execute the example with: `python main.py` or `python3 main.py`.

### Agent

- Simple - [examples/agent/simple](https://github.com/deepgram/deepgram-python-sdk/blob/main/examples/agent/simple/main.py)
- Async Simple - [examples/agent/async_simple](https://github.com/deepgram/deepgram-python-sdk/blob/main/examples/agent/async_simple/main.py)

### Text to Speech

- Asynchronous - [examples/text-to-speech](https://github.com/deepgram/deepgram-python-sdk/blob/main/examples/text-to-speech/rest/file/async_hello_world/main.py)
- Synchronous - [examples/text-to-speech](https://github.com/deepgram/deepgram-python-sdk/blob/main/examples/text-to-speech/rest/file/hello_world/main.py)

### Analyze Text

- Intent Recognition - [examples/analyze/intent](https://github.com/deepgram/deepgram-python-sdk/blob/main/examples/analyze/intent/main.py)
- Sentiment Analysis - [examples/sentiment/intent](https://github.com/deepgram/deepgram-python-sdk/blob/main/examples/analyze/sentiment/main.py)
- Summarization - [examples/analyze/intent](https://github.com/deepgram/deepgram-python-sdk/blob/main/examples/analyze/summary/main.py)
- Topic Detection - [examples/analyze/intent](https://github.com/deepgram/deepgram-python-sdk/blob/main/examples/analyze/topic/main.py)

### PreRecorded Audio

- Transcription From an Audio File - [examples/prerecorded/file](https://github.com/deepgram/deepgram-python-sdk/blob/main/examples/speech-to-text/rest/file/main.py)
- Transcription From an URL - [examples/prerecorded/url](https://github.com/deepgram/deepgram-python-sdk/blob/main/examples/speech-to-text/rest/url/main.py)
- Intent Recognition - [examples/speech-to-text/rest/intent](https://github.com/deepgram/deepgram-python-sdk/blob/main/examples/speech-to-text/rest/intent/main.py)
- Sentiment Analysis - [examples/speech-to-text/rest/sentiment](https://github.com/deepgram/deepgram-python-sdk/blob/main/examples/speech-to-text/rest/sentiment/main.py)
- Summarization - [examples/speech-to-text/rest/summary](https://github.com/deepgram/deepgram-python-sdk/blob/main/examples/speech-to-text/rest/summary/main.py)
- Topic Detection - [examples/speech-to-text/rest/topic](https://github.com/deepgram/deepgram-python-sdk/blob/main/examples/speech-to-text/rest/topic/main.py)

### Live Audio Transcription

- From a Microphone - [examples/streaming/microphone](https://github.com/deepgram/deepgram-python-sdk/blob/main/examples/speech-to-text/rest/stream_file/main.py)
- From an HTTP Endpoint - [examples/streaming/http](https://github.com/deepgram/deepgram-python-sdk/blob/main/examples/speech-to-text/rest/async_url/main.py)

Management API exercise the full [CRUD](https://en.wikipedia.org/wiki/Create,_read,_update_and_delete) operations for:

- Balances - [examples/manage/balances](https://github.com/deepgram/deepgram-python-sdk/blob/main/examples/manage/balances/main.py)
- Invitations - [examples/manage/invitations](https://github.com/deepgram/deepgram-python-sdk/blob/main/examples/manage/invitations/main.py)
- Keys - [examples/manage/keys](https://github.com/deepgram/deepgram-python-sdk/blob/main/examples/manage/keys/main.py)
- Members - [examples/manage/members](https://github.com/deepgram/deepgram-python-sdk/blob/main/examples/manage/members/main.py)
- Projects - [examples/manage/projects](https://github.com/deepgram/deepgram-python-sdk/blob/main/examples/manage/projects/main.py)
- Scopes - [examples/manage/scopes](https://github.com/deepgram/deepgram-python-sdk/blob/main/examples/manage/scopes/main.py)
- Usage - [examples/manage/usage](https://github.com/deepgram/deepgram-python-sdk/blob/main/examples/manage/usage/main.py)

## Logging

This SDK provides logging as a means to troubleshoot and debug issues encountered. By default, this SDK will enable `Information` level messages and higher (ie `Warning`, `Error`, etc) when you initialize the library as follows:

```python
deepgram: DeepgramClient = DeepgramClient()
```

To increase the logging output/verbosity for debug or troubleshooting purposes, you can set the `DEBUG` level but using this code:

```python
config: DeepgramClientOptions = DeepgramClientOptions(
    verbose=logging.DEBUG,
)
deepgram: DeepgramClient = DeepgramClient("", config)
```

## Backwards Compatibility

Older SDK versions will receive Priority 1 (P1) bug support only. Security issues, both in our code and dependencies, are promptly addressed. Significant bugs without clear workarounds are also given priority attention.

## Development and Contributing

Interested in contributing? We ❤️ pull requests!

To make sure our community is safe for all, be sure to review and agree to our
[Code of Conduct](https://github.com/deepgram/deepgram-python-sdk/blob/main/.github/CODE_OF_CONDUCT.md). Then see the
[Contribution](https://github.com/deepgram/deepgram-python-sdk/blob/main/.github/CONTRIBUTING.md) guidelines for more information.

### Prerequisites

In order to develop new features for the SDK itself, you first need to uninstall any previous installation of the `deepgram-sdk` and then install/pip the dependencies contained in the `requirements.txt` then instruct python (via pip) to use the SDK by installing it locally.

From the root of the repo, that would entail:

```bash
pip uninstall deepgram-sdk
pip install -r requirements.txt
pip install -e .
```

### Daily and Unit Tests

If you are looking to use, run, contribute or modify to the daily/unit tests, then you need to install the following dependencies:

```bash
pip install -r requirements-dev.txt
```

#### Daily Tests

The daily tests invoke a series of checks against the actual/real API endpoint and save the results in the `tests/response_data` folder. This response data is updated nightly to reflect the latest response from the server. Running the daily tests does require a `DEEPGRAM_API_KEY` set in your environment variables.

To run the Daily Tests:

```bash
make daily-test
```

#### Unit Tests

The unit tests invoke a series of checks against mock endpoints using the responses saved in `tests/response_data` from the daily tests. These tests are meant to simulate running against the endpoint without actually reaching out to the endpoint; running the unit tests does require a `DEEPGRAM_API_KEY` set in your environment variables, but you will not actually reach out to the server.

```bash
make unit-test
```

## Getting Help

We love to hear from you so if you have questions, comments or find a bug in the
project, let us know! You can either:

- [Open an issue in this repository](https://github.com/deepgram/deepgram-python-sdk/issues/new)
- [Join the Deepgram Github Discussions Community](https://github.com/orgs/deepgram/discussions)
- [Join the Deepgram Discord Community](https://discord.gg/xWRaCDBtW4)


================================================
File: CODE_OF_CONDUCT.md
================================================
# Code of Conduct

Please see the [Code of Conduct](https://github.com/deepgram/deepgram-python-sdk/blob/main/.github/CODE_OF_CONDUCT.md) at [https://github.com/deepgram/deepgram-python-sdk/blob/main/.github/CODE_OF_CONDUCT.md](https://github.com/deepgram/deepgram-python-sdk/blob/main/.github/CODE_OF_CONDUCT.md).


================================================
File: CONTRIBUTING.md
================================================
# Contributing Guidelines

Please see the [Contributing Guidelines](https://github.com/deepgram/deepgram-python-sdk/blob/main/.github/CONTRIBUTING.md) at [https://github.com/deepgram/deepgram-python-sdk/blob/main/.github/CONTRIBUTING.md](https://github.com/deepgram/deepgram-python-sdk/blob/main/.github/CONTRIBUTING.md).


================================================
File: LICENSE
================================================
MIT License

Copyright (c) 2021 deepgram

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.


================================================
File: Makefile
================================================
# Copyright 2024 Deepgram SDK contributors. All Rights Reserved.
# Use of this source code is governed by a MIT license that can be found in the LICENSE file.
# SPDX-License-Identifier: MIT

# detect the build OS
ifeq ($(OS),Windows_NT)
	build_OS := Windows
	NUL = NUL
else
	build_OS := $(shell uname -s 2>/dev/null || echo Unknown)
	NUL = /dev/null
endif

.DEFAULT_GOAL:=help

##### GLOBAL
ROOT_DIR := $(shell git rev-parse --show-toplevel)

# Add tooling binaries here and in hack/tools/Makefile
TOOLS_BIN_DIR := $(shell mktemp -d)

help: #### Display help
	@echo ''
	@echo 'Syntax: make <target>'
	@awk 'BEGIN {FS = ":.*## "; printf "\nTargets:\n"} /^[a-zA-Z_-]+:.*?#### / { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)
	@echo ''
##### GLOBAL

##### LINTING TARGETS
.PHONY: version
version: #### display version of components
	@echo 'ROOT_DIR: $(ROOT_DIR)'
	@echo 'GOOS: $(GOOS)'
	@echo 'GOARCH: $(GOARCH)'
	@echo 'go version: $(shell go version)'

.PHONY: check lint pylint format black blackformat lint-files lint-diff static mypy mdlint shellcheck actionlint yamllint ### Performs all of the checks, lint'ing, etc available
check: lint static mdlint shellcheck actionlint yamllint

.PHONY: ensure-deps
ensure-deps: #### Ensure that all required dependency utilities are downloaded or installed
	hack/ensure-deps/ensure-dependencies.sh

GO_MODULES=$(shell find . -path "*/go.mod" | xargs -I _ dirname _)

PYTHON_FILES=.
lint-files: PYTHON_FILES=deepgram/ examples/
lint-diff: PYTHON_FILES=$(shell git diff --name-only --diff-filter=d main | grep -E '\.py$$')

lint-files lint-diff: #### Performs Python formatting
	black --target-version py310 $(PYTHON_FILES)

black blackformat format: lint-files

pylint: lint-files #### Performs Python linting
	pylint --disable=W0622 --disable=W0404 --disable=W0611 --rcfile .pylintrc deepgram

lint: pylint #### Performs Golang programming lint

static mypy: #### Performs static analysis
	mypy --config-file mypy.ini --python-version 3.10 --exclude tests --exclude examples $(PYTHON_FILES)

mdlint: #### Performs Markdown lint
	# mdlint rules with common errors and possible fixes can be found here:
	# https://github.com/DavidAnson/markdownlint/blob/main/doc/Rules.md
	hack/check/check-mdlint.sh

shellcheck: #### Performs bash/shell lint
	hack/check/check-shell.sh

yamllint: #### Performs yaml lint
	hack/check/check-yaml.sh

actionlint: #### Performs GitHub Actions lint
	actionlint
##### LINTING TARGETS

##### TESTING TARGETS

.PHONY: test daily-test unit-test
test: #### Run ALL tests
	@echo "Running ALL tests"
	python -m pytest

daily-test: #### Run daily tests
	@echo "Running daily tests"
	python -m pytest -k daily_test

unit-test: #### Run unit tests
	@echo "Running unit tests"
	python -m pytest -k unit_test
##### TESTING TARGETS

================================================
File: mypy.ini
================================================
# MyPy config file
# File reference here - http://mypy.readthedocs.io/en/latest/config_file.html#config-file

[mypy]
warn_redundant_casts = True
warn_unused_ignores = True

# Needed because of bug in MyPy
disallow_subclassing_any = False

mypy_path = stubs

[mypy-*]
disallow_untyped_calls = True
disallow_untyped_defs = True
check_untyped_defs = True
warn_return_any = True
no_implicit_optional = True
strict_optional = True
ignore_missing_imports = True

[mypy-setuptools]
ignore_missing_imports = True

[mypy-aenum]
ignore_missing_imports = True


================================================
File: pyproject.toml
================================================
######
# general configuration
######
[build-system]
requires = ["setuptools", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "deepgram-sdk"
dynamic = ["version", "description", "readme", "license", "authors", "keywords", "classifiers", "dependencies"]

[tool.setuptools.dynamic]
version = {attr = "deepgram.__version__"}

######
# poetry configuration
######
# [build-system]
# requires = ["poetry-core"]
# build-backend = "poetry.core.masonry.api"

# poetry configuration
[tool.poetry]
name = "deepgram"
version = "3.X.Y" # Please update this to the version you are using
description = "The official Python SDK for the Deepgram automated speech recognition platform."
authors = ["Deepgram DevRel <devrel@deepgram.com>"]
license = "MIT"
readme = "README.md"

[tool.poetry.dependencies]
python = "^3.10"
httpx = "^0.25.2"
websockets = ">=12.0"
typing-extensions = "^4.9.0"
dataclasses-json = "^0.6.3"
aiohttp = "^3.9.1"
aiofiles = "^23.2.1"
aenum = "^3.1.0"
deprecation = "^2.1.0"
# needed only if you are looking to develop/work-on the SDK
# black = "^24.0"
# pylint = "^3.0"
# mypy = "^1.0"
# types-pyaudio = "^0.2.16"
# types-aiofiles = "^23.2.0"
# needed only if you are looking to use samples in the "examples" folder
# pyaudio = "^0.2.14"
# python-dotenv = "^1.0.0"
# needed for contributing to the SDK
# pytest-asyncio = "^0.21.1"
# pytest = "^7.4.3"
# fuzzywuzzy = "^0.18.0"
# pytest-cov = "^4.1.0"

# [tool.poetry.group.dev.dependencies]
# fuzzywuzzy = "^0.18.0"


================================================
File: requirements-dev.txt
================================================
# pip install -r requirements.txt

# additional requirements for development
soundfile==0.12.1
numpy==2.0.1
websocket-server==0.6.4

# lint, static, etc
black==24.*
pylint==3.*
mypy==1.*

# static check types
types-pyaudio
types-aiofiles

# Testing
pytest
pytest-asyncio
fuzzywuzzy
pytest-cov

================================================
File: requirements.txt
================================================
# pip install -r requirements.txt

# standard libs
websockets>=12.0
httpx==0.*
dataclasses-json==0.*
dataclasses==0.*
typing_extensions==4.*
aenum==3.*
deprecation==2.*

# Async functionality, likely to be already installed
aiohttp==3.*
aiofiles==23.*


================================================
File: setup.py
================================================
# Copyright 2023-2024 Deepgram SDK contributors. All Rights Reserved.
# Use of this source code is governed by a MIT license that can be found in the LICENSE file.
# SPDX-License-Identifier: MIT

from setuptools import setup, find_packages
import os.path
import sys

if sys.version_info < (3, 10):
    sys.exit("Sorry, Python < 3.10 is not supported")

with open("README.md", "r", encoding="utf-8") as fh:
    LONG_DESCRIPTION = fh.read()

DESCRIPTION = (
    "The official Python SDK for the Deepgram automated speech recognition platform."
)

setup(
    name="deepgram-sdk",
    author="Deepgram",
    author_email="devrel@deepgram.com",
    url="https://github.com/deepgram/deepgram-python-sdk",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    license="MIT",
    packages=find_packages(exclude=["tests"]),
    install_requires=[
        "httpx>=0.25.2",
        "websockets>=12.0",
        "dataclasses-json>=0.6.3",
        "typing_extensions>=4.9.0",
        "aiohttp>=3.9.1",
        "aiofiles>=23.2.1",
        "aenum>=3.1.0",
        "deprecation>=2.1.0",
    ],
    keywords=["deepgram", "deepgram speech-to-text"],
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
    ],
)


================================================
File: .env.example
================================================
DG_API_KEY=""
DG_PROJECT_ID=""


================================================
File: .markdownlintrc
================================================
{
  "default": true,
  "line_length": false,
  "MD024": { "allow_different_nesting": true },
  "MD026": { "punctuation": ".,;:!" },
  "MD046": { "style": "fenced" }
}


================================================
File: .pylintrc
================================================
[MAIN]

# Analyse import fallback blocks. This can be used to support both Python 2 and
# 3 compatible code, which means that the block might have code that exists
# only in one or another interpreter, leading to false positives when analysed.
analyse-fallback-blocks=no

# Clear in-memory caches upon conclusion of linting. Useful if running pylint
# in a server-like mode.
clear-cache-post-run=no

# Load and enable all available extensions. Use --list-extensions to see a list
# all available extensions.
#enable-all-extensions=

# In error mode, messages with a category besides ERROR or FATAL are
# suppressed, and no reports are done by default. Error mode is compatible with
# disabling specific errors.
#errors-only=

# Always return a 0 (non-error) status code, even if lint errors are found.
# This is primarily useful in continuous integration scripts.
#exit-zero=

# A comma-separated list of package or module names from where C extensions may
# be loaded. Extensions are loading into the active Python interpreter and may
# run arbitrary code.
extension-pkg-allow-list=

# A comma-separated list of package or module names from where C extensions may
# be loaded. Extensions are loading into the active Python interpreter and may
# run arbitrary code. (This is an alternative name to extension-pkg-allow-list
# for backward compatibility.)
extension-pkg-whitelist=

# Return non-zero exit code if any of these messages/categories are detected,
# even if score is above --fail-under value. Syntax same as enable. Messages
# specified are enabled, while categories only check already-enabled messages.
fail-on=

# Specify a score threshold under which the program will exit with error.
fail-under=10

# Interpret the stdin as a python script, whose filename needs to be passed as
# the module_or_package argument.
#from-stdin=

# Files or directories to be skipped. They should be base names, not paths.
ignore=.git

# Add files or directories matching the regular expressions patterns to the
# ignore-list. The regex matches against paths and can be in Posix or Windows
# format. Because '\\' represents the directory delimiter on Windows systems,
# it can't be used as an escape character.
ignore-paths=

# Files or directories matching the regular expression patterns are skipped.
# The regex matches against base names, not paths. The default value ignores
# Emacs file locks
ignore-patterns=^\.#

# List of module names for which member attributes should not be checked and
# will not be imported (useful for modules/projects where namespaces are
# manipulated during runtime and thus existing member attributes cannot be
# deduced by static analysis). It supports qualified module names, as well as
# Unix pattern matching.
ignored-modules=

# Python code to execute, usually for sys.path manipulation such as
# pygtk.require().
#init-hook=

# Use multiple processes to speed up Pylint. Specifying 0 will auto-detect the
# number of processors available to use, and will cap the count on Windows to
# avoid hangs.
jobs=4

# Control the amount of potential inferred values when inferring a single
# object. This can help the performance when dealing with large functions or
# complex, nested conditions.
limit-inference-results=100

# List of plugins (as comma separated values of python module names) to load,
# usually to register additional checkers.
load-plugins=

# Pickle collected data for later comparisons.
persistent=yes

# Resolve imports to .pyi stubs if available. May reduce no-member messages and
# increase not-an-iterable messages.
prefer-stubs=no

# Minimum Python version to use for version dependent checks. Will default to
# the version used to run pylint.
py-version=3.10

# Discover python modules and packages in the file system subtree.
recursive=no

# Add paths to the list of the source roots. Supports globbing patterns. The
# source root is an absolute path or a path relative to the current working
# directory used to determine a package namespace for modules located under the
# source root.
source-roots=

# When enabled, pylint would attempt to guess common misconfiguration and emit
# user-friendly hints instead of false-positive error messages.
suggestion-mode=yes

# Allow loading of arbitrary C extensions. Extensions are imported into the
# active Python interpreter and may run arbitrary code.
unsafe-load-any-extension=no

# In verbose mode, extra non-checker-related info will be displayed.
#verbose=


[BASIC]

# Naming style matching correct argument names.
argument-naming-style=snake_case

# Regular expression matching correct argument names. Overrides argument-
# naming-style. If left empty, argument names will be checked with the set
# naming style.
#argument-rgx=

# Naming style matching correct attribute names.
attr-naming-style=snake_case

# Regular expression matching correct attribute names. Overrides attr-naming-
# style. If left empty, attribute names will be checked with the set naming
# style.
#attr-rgx=

# Bad variable names which should always be refused, separated by a comma.
bad-names=foo,
          bar,
          baz,
          toto,
          tutu,
          tata

# Bad variable names regexes, separated by a comma. If names match any regex,
# they will always be refused
bad-names-rgxs=

# Naming style matching correct class attribute names.
class-attribute-naming-style=any

# Regular expression matching correct class attribute names. Overrides class-
# attribute-naming-style. If left empty, class attribute names will be checked
# with the set naming style.
#class-attribute-rgx=

# Naming style matching correct class constant names.
class-const-naming-style=UPPER_CASE

# Regular expression matching correct class constant names. Overrides class-
# const-naming-style. If left empty, class constant names will be checked with
# the set naming style.
#class-const-rgx=

# Naming style matching correct class names.
class-naming-style=PascalCase

# Regular expression matching correct class names. Overrides class-naming-
# style. If left empty, class names will be checked with the set naming style.
#class-rgx=

# Naming style matching correct constant names.
const-naming-style=UPPER_CASE

# Regular expression matching correct constant names. Overrides const-naming-
# style. If left empty, constant names will be checked with the set naming
# style.
#const-rgx=

# Minimum line length for functions/classes that require docstrings, shorter
# ones are exempt.
docstring-min-length=-1

# Naming style matching correct function names.
function-naming-style=snake_case

# Regular expression matching correct function names. Overrides function-
# naming-style. If left empty, function names will be checked with the set
# naming style.
#function-rgx=

# Good variable names which should always be accepted, separated by a comma.
good-names=i,
           j,
           k,
           ex,
           Run,
           _

# Good variable names regexes, separated by a comma. If names match any regex,
# they will always be accepted
good-names-rgxs=

# Include a hint for the correct naming format with invalid-name.
include-naming-hint=no

# Naming style matching correct inline iteration names.
inlinevar-naming-style=any

# Regular expression matching correct inline iteration names. Overrides
# inlinevar-naming-style. If left empty, inline iteration names will be checked
# with the set naming style.
#inlinevar-rgx=

# Naming style matching correct method names.
method-naming-style=snake_case

# Regular expression matching correct method names. Overrides method-naming-
# style. If left empty, method names will be checked with the set naming style.
#method-rgx=

# Naming style matching correct module names.
module-naming-style=snake_case

# Regular expression matching correct module names. Overrides module-naming-
# style. If left empty, module names will be checked with the set naming style.
#module-rgx=

# Colon-delimited sets of names that determine each other's naming style when
# the name regexes allow several styles.
name-group=

# Regular expression which should only match function or class names that do
# not require a docstring.
no-docstring-rgx=^_

# List of decorators that produce properties, such as abc.abstractproperty. Add
# to this list to register other decorators that produce valid properties.
# These decorators are taken in consideration only for invalid-name.
property-classes=abc.abstractproperty

# Regular expression matching correct type alias names. If left empty, type
# alias names will be checked with the set naming style.
#typealias-rgx=

# Regular expression matching correct type variable names. If left empty, type
# variable names will be checked with the set naming style.
#typevar-rgx=

# Naming style matching correct variable names.
variable-naming-style=snake_case

# Regular expression matching correct variable names. Overrides variable-
# naming-style. If left empty, variable names will be checked with the set
# naming style.
#variable-rgx=


[CLASSES]

# Warn about protected attribute access inside special methods
check-protected-access-in-special-methods=no

# List of method names used to declare (i.e. assign) instance attributes.
defining-attr-methods=__init__,
                      __new__,
                      setUp,
                      asyncSetUp,
                      __post_init__

# List of member names, which should be excluded from the protected access
# warning.
exclude-protected=_asdict,_fields,_replace,_source,_make,os._exit

# List of valid names for the first argument in a class method.
valid-classmethod-first-arg=cls

# List of valid names for the first argument in a metaclass class method.
valid-metaclass-classmethod-first-arg=mcs


[DESIGN]

# List of regular expressions of class ancestor names to ignore when counting
# public methods (see R0903)
exclude-too-few-public-methods=

# List of qualified class names to ignore when counting class parents (see
# R0901)
ignored-parents=

# Maximum number of arguments for function / method.
max-args=5

# Maximum number of attributes for a class (see R0902).
max-attributes=7

# Maximum number of boolean expressions in an if statement (see R0916).
max-bool-expr=5

# Maximum number of branch for function / method body.
max-branches=12

# Maximum number of locals for function / method body.
max-locals=15

# Maximum number of parents for a class (see R0901).
max-parents=7

# Maximum number of public methods for a class (see R0904).
max-public-methods=20

# Maximum number of return / yield for function / method body.
max-returns=6

# Maximum number of statements in function / method body.
max-statements=50

# Minimum number of public methods for a class (see R0903).
min-public-methods=2


[EXCEPTIONS]

# Exceptions that will emit a warning when caught.
overgeneral-exceptions=builtins.BaseException,builtins.Exception


[FORMAT]

# Expected format of line ending, e.g. empty (any line ending), LF or CRLF.
expected-line-ending-format=

# Regexp for a line that is allowed to be longer than the limit.
ignore-long-lines=^\s*(# )?<?https?://\S+>?$

# Number of spaces of indent required inside a hanging or continued line.
indent-after-paren=4

# String used as indentation unit. This is usually "    " (4 spaces) or "\t" (1
# tab).
indent-string='    '

# Maximum number of characters on a single line.
max-line-length=100

# Maximum number of lines in a module.
max-module-lines=1000

# Allow the body of a class to be on the same line as the declaration if body
# contains single statement.
single-line-class-stmt=no

# Allow the body of an if to be on the same line as the test if there is no
# else.
single-line-if-stmt=no


[IMPORTS]

# List of modules that can be imported at any level, not just the top level
# one.
allow-any-import-level=

# Allow explicit reexports by alias from a package __init__.
allow-reexport-from-package=no

# Allow wildcard imports from modules that define __all__.
allow-wildcard-with-all=no

# Deprecated modules which should not be used, separated by a comma.
deprecated-modules=

# Output a graph (.gv or any supported image format) of external dependencies
# to the given file (report RP0402 must not be disabled).
ext-import-graph=

# Output a graph (.gv or any supported image format) of all (i.e. internal and
# external) dependencies to the given file (report RP0402 must not be
# disabled).
import-graph=

# Output a graph (.gv or any supported image format) of internal dependencies
# to the given file (report RP0402 must not be disabled).
int-import-graph=

# Force import order to recognize a module as part of the standard
# compatibility libraries.
known-standard-library=

# Force import order to recognize a module as part of a third party library.
known-third-party=enchant

# Couples of modules and preferred modules, separated by a comma.
preferred-modules=


[LOGGING]

# The type of string formatting that logging methods do. `old` means using %
# formatting, `new` is for `{}` formatting.
logging-format-style=old

# Logging modules to check that the string format arguments are in logging
# function parameter format.
logging-modules=logging


[MESSAGES CONTROL]

# Only show warnings with the listed confidence levels. Leave empty to show
# all. Valid levels: HIGH, CONTROL_FLOW, INFERENCE, INFERENCE_FAILURE,
# UNDEFINED.
confidence=HIGH,
           CONTROL_FLOW,
           INFERENCE,
           INFERENCE_FAILURE,
           UNDEFINED

# Disable the message, report, category or checker with the given id(s). You
# can either give multiple identifiers separated by comma (,) or put this
# option multiple times (only on the command line, not in the configuration
# file where it should appear only once). You can also use "--disable=all" to
# disable everything first and then re-enable specific checks. For example, if
# you want to run only the similarities checker, you can use "--disable=all
# --enable=similarities". If you want to run only the classes checker, but have
# no Warning level messages displayed, use "--disable=all --enable=classes
# --disable=W".
disable=raw-checker-failed,
        bad-inline-option,
        locally-disabled,
        file-ignored,
        suppressed-message,
        useless-suppression,
        deprecated-pragma,
        use-symbolic-message-instead,
        use-implicit-booleaness-not-comparison-to-string,
        use-implicit-booleaness-not-comparison-to-zero,
        line-too-long,
        missing-module-docstring,
        too-many-arguments,
        too-few-public-methods,
        cyclic-import,
        duplicate-code

# sample from k8s
# disable=import-star-module-level,
#         old-octal-literal,
#         oct-method,
#         print-statement,
#         unpacking-in-except,
#         parameter-unpacking,
#         backtick,
#         old-raise-syntax,
#         old-ne-operator,
#         long-suffix,
#         dict-view-method,
#         dict-iter-method,
#         metaclass-assignment,
#         next-method-called,
#         raising-string,
#         indexing-exception,
#         raw_input-builtin,
#         long-builtin,
#         file-builtin,
#         execfile-builtin,
#         coerce-builtin,
#         cmp-builtin,
#         buffer-builtin,
#         basestring-builtin,
#         apply-builtin,
#         filter-builtin-not-iterating,
#         using-cmp-argument,
#         useless-suppression,
#         range-builtin-not-iterating,
#         suppressed-message,
#         missing-docstring,
#         no-absolute-import,
#         old-division,
#         cmp-method,
#         reload-builtin,
#         zip-builtin-not-iterating,
#         intern-builtin,
#         unichr-builtin,
#         reduce-builtin,
#         standarderror-builtin,
#         unicode-builtin,
#         xrange-builtin,
#         coerce-method,
#         delslice-method,
#         getslice-method,
#         setslice-method,
#         input-builtin,
#         round-builtin,
#         hex-method,
#         nonzero-method,
#         map-builtin-not-iterating,
#         relative-import,
#         invalid-name,
#         bad-continuation,
#         no-member,
#         locally-disabled,
#         fixme,
#         import-error,
#         too-many-locals,
#         no-name-in-module,
#         too-many-instance-attributes,
#         no-self-use,
#         logging-fstring-interpolation


# Enable the message, report, category or checker with the given id(s). You can
# either give multiple identifier separated by comma (,) or put this option
# multiple time (only on the command line, not in the configuration file where
# it should appear only once). See also the "--disable" option for examples.
enable=


[METHOD_ARGS]

# List of qualified names (i.e., library.method) which require a timeout
# parameter e.g. 'requests.api.get,requests.api.post'
timeout-methods=requests.api.delete,requests.api.get,requests.api.head,requests.api.options,requests.api.patch,requests.api.post,requests.api.put,requests.api.request


[MISCELLANEOUS]

# List of note tags to take in consideration, separated by a comma.
notes=FIXME,
      XXX,
      TODO

# Regular expression of note tags to take in consideration.
notes-rgx=


[REFACTORING]

# Maximum number of nested blocks for function / method body
max-nested-blocks=5

# Complete name of functions that never returns. When checking for
# inconsistent-return-statements if a never returning function is called then
# it will be considered as an explicit return statement and no message will be
# printed.
never-returning-functions=sys.exit,argparse.parse_error

# Let 'consider-using-join' be raised when the separator to join on would be
# non-empty (resulting in expected fixes of the type: ``"- " + " -
# ".join(items)``)
suggest-join-with-non-empty-separator=yes


[REPORTS]

# Python expression which should return a score less than or equal to 10. You
# have access to the variables 'fatal', 'error', 'warning', 'refactor',
# 'convention', and 'info' which contain the number of messages in each
# category, as well as 'statement' which is the total number of statements
# analyzed. This score is used by the global evaluation report (RP0004).
evaluation=max(0, 0 if fatal else 10.0 - ((float(5 * error + warning + refactor + convention) / statement) * 10))

# Template used to display messages. This is a python new-style format string
# used to format the message information. See doc for all details.
msg-template=

# Set the output format. Available formats are: text, parseable, colorized,
# json2 (improved json format), json (old json format) and msvs (visual
# studio). You can also give a reporter class, e.g.
# mypackage.mymodule.MyReporterClass.
#output-format=

# Tells whether to display a full report or only the messages.
reports=no

# Activate the evaluation score.
score=yes


[SIMILARITIES]

# Comments are removed from the similarity computation
ignore-comments=yes

# Docstrings are removed from the similarity computation
ignore-docstrings=yes

# Imports are removed from the similarity computation
ignore-imports=yes

# Signatures are removed from the similarity computation
ignore-signatures=yes

# Minimum lines number of a similarity.
min-similarity-lines=4


[SPELLING]

# Limits count of emitted suggestions for spelling mistakes.
max-spelling-suggestions=4

# Spelling dictionary name. No available dictionaries : You need to install
# both the python package and the system dependency for enchant to work.
spelling-dict=

# List of comma separated words that should be considered directives if they
# appear at the beginning of a comment and should not be checked.
spelling-ignore-comment-directives=fmt: on,fmt: off,noqa:,noqa,nosec,isort:skip,mypy:

# List of comma separated words that should not be checked.
spelling-ignore-words=

# A path to a file that contains the private dictionary; one word per line.
spelling-private-dict-file=

# Tells whether to store unknown words to the private dictionary (see the
# --spelling-private-dict-file option) instead of raising a message.
spelling-store-unknown-words=no


[STRING]

# This flag controls whether inconsistent-quotes generates a warning when the
# character used as a quote delimiter is used inconsistently within a module.
check-quote-consistency=no

# This flag controls whether the implicit-str-concat should generate a warning
# on implicit string concatenation in sequences defined over several lines.
check-str-concat-over-line-jumps=no


[TYPECHECK]

# List of decorators that produce context managers, such as
# contextlib.contextmanager. Add to this list to register other decorators that
# produce valid context managers.
contextmanager-decorators=contextlib.contextmanager

# List of members which are set dynamically and missed by pylint inference
# system, and so shouldn't trigger E1101 when accessed. Python regular
# expressions are accepted.
generated-members=

# Tells whether to warn about missing members when the owner of the attribute
# is inferred to be None.
ignore-none=yes

# This flag controls whether pylint should warn about no-member and similar
# checks whenever an opaque object is returned when inferring. The inference
# can return multiple potential results while evaluating a Python object, but
# some branches might not be evaluated, which results in partial inference. In
# that case, it might be useful to still emit no-member and other checks for
# the rest of the inferred objects.
ignore-on-opaque-inference=yes

# List of symbolic message names to ignore for Mixin members.
ignored-checks-for-mixins=no-member,
                          not-async-context-manager,
                          not-context-manager,
                          attribute-defined-outside-init

# List of class names for which member attributes should not be checked (useful
# for classes with dynamically set attributes). This supports the use of
# qualified names.
ignored-classes=optparse.Values,
    thread._local,
    _thread._local,
    argparse.Namespace

# Show a hint with possible names when a member name was not found. The aspect
# of finding the hint is based on edit distance.
missing-member-hint=yes

# The minimum edit distance a name should have in order to be considered a
# similar match for a missing member name.
missing-member-hint-distance=1

# The total number of similar names that should be taken in consideration when
# showing a hint for a missing member.
missing-member-max-choices=1

# Regex pattern to define which classes are considered mixins.
mixin-class-rgx=.*[Mm]ixin

# List of decorators that change the signature of a decorated function.
signature-mutators=


[VARIABLES]

# List of additional names supposed to be defined in builtins. Remember that
# you should avoid defining new builtins when possible.
additional-builtins=

# Tells whether unused global variables should be treated as a violation.
allow-global-unused-variables=yes

# List of names allowed to shadow builtins
allowed-redefined-builtins=

# List of strings which can identify a callback function by name. A callback
# name must start or end with one of those strings.
callbacks=cb_,
          _cb

# A regular expression matching the name of dummy variables (i.e. expected to
# not be used).
dummy-variables-rgx=_+$|(_[a-zA-Z0-9_]*[a-zA-Z0-9]+?$)|dummy|^ignored_|^unused_

# Argument names that match this expression will be ignored.
ignored-argument-names=_.*|^ignored_|^unused_

# Tells whether we should check for unused import in __init__ files.
init-import=no

# List of qualified module names which can have objects that can redefine
# builtins.
redefining-builtins-modules=six.moves,past.builtins,future.builtins,builtins,io


================================================
File: .yamllintconfig.yaml
================================================
---
extends: relaxed

rules:
  line-length: disable
  trailing-spaces: enable
  new-line-at-end-of-file: enable
  new-lines:
    type: unix
  indentation: disable
  key-duplicates: disable
  empty-lines: enable
  colons: disable
  commas: disable

ignore: |
  /deepgram-python-sdk/.github/ISSUE_TEMPLATE/config.yml
  /deepgram-python-sdk/addons/**/*/


================================================
File: deepgram/__init__.py
================================================
# Copyright 2023-2024 Deepgram SDK contributors. All Rights Reserved.
# Use of this source code is governed by a MIT license that can be found in the LICENSE file.
# SPDX-License-Identifier: MIT

# version
__version__ = "0.0.0"

# entry point for the deepgram python sdk
import logging
from .utils import VerboseLogger
from .utils import (
    NOTICE,
    SPAM,
    SUCCESS,
    VERBOSE,
    WARNING,
    ERROR,
    FATAL,
    CRITICAL,
    INFO,
    DEBUG,
    NOTSET,
)

from .client import Deepgram, DeepgramClient
from .client import DeepgramClientOptions, ClientOptionsFromEnv
from .client import (
    DeepgramError,
    DeepgramTypeError,
    DeepgramModuleError,
    DeepgramApiError,
    DeepgramUnknownApiError,
)
from .errors import DeepgramApiKeyError

# listen/read client
from .client import ListenRouter, ReadRouter, SpeakRouter, AgentRouter

# common
from .client import (
    TextSource,
    BufferSource,
    StreamSource,
    FileSource,
    UrlSource,
)
from .client import BaseResponse
from .client import (
    Average,
    Intent,
    Intents,
    IntentsInfo,
    Segment,
    SentimentInfo,
    Sentiment,
    Sentiments,
    SummaryInfo,
    Topic,
    Topics,
    TopicsInfo,
)
from .client import (
    ModelInfo,
    Hit,
    Search,
)
from .client import (
    OpenResponse,
    CloseResponse,
    UnhandledResponse,
    ErrorResponse,
)

# speect-to-text WS
from .client import LiveClient, AsyncLiveClient  # backward compat
from .client import ListenWebSocketClient, AsyncListenWebSocketClient
from .client import LiveTranscriptionEvents
from .client import LiveOptions, ListenWebSocketOptions
from .client import (
    #### top level
    LiveResultResponse,
    ListenWSMetadataResponse,
    SpeechStartedResponse,
    UtteranceEndResponse,
    #### common websocket response
    # OpenResponse,
    # CloseResponse,
    # UnhandledResponse,
    # ErrorResponse,
    #### unique
    ListenWSMetadata,
    ListenWSAlternative,
    ListenWSChannel,
    ListenWSWord,
)

# prerecorded
from .client import PreRecordedClient, AsyncPreRecordedClient  # backward compat
from .client import ListenRESTClient, AsyncListenRESTClient
from .client import (
    # common
    # UrlSource,
    # BufferSource,
    # StreamSource,
    # TextSource,
    # FileSource,
    # unique
    PreRecordedStreamSource,
    PrerecordedSource,
    ListenRestSource,
    SpeakRESTSource,
)
from .client import (
    ListenRESTOptions,
    PrerecordedOptions,
)
from .client import (
    #### top level
    AsyncPrerecordedResponse,
    PrerecordedResponse,
    SyncPrerecordedResponse,
    #### shared
    # Average,
    # Alternative,
    # Channel,
    # Intent,
    # Intents,
    # IntentsInfo,
    # Segment,
    # SentimentInfo,
    # Sentiment,
    # Sentiments,
    # SummaryInfo,
    # Topic,
    # Topics,
    # TopicsInfo,
    # Word,
    #### unique
    Entity,
    Hit,
    ListenRESTMetadata,
    ModelInfo,
    Paragraph,
    Paragraphs,
    ListenRESTResults,
    Search,
    Sentence,
    Summaries,
    SummaryV1,
    SummaryV2,
    Translation,
    Utterance,
    Warning,
    ListenRESTAlternative,
    ListenRESTChannel,
    ListenRESTWord,
)

# read
from .client import ReadClient, AsyncReadClient
from .client import AnalyzeClient, AsyncAnalyzeClient
from .client import (
    AnalyzeOptions,
    AnalyzeStreamSource,
    AnalyzeSource,
)
from .client import (
    #### top level
    AsyncAnalyzeResponse,
    SyncAnalyzeResponse,
    AnalyzeResponse,
    #### shared
    # Average,
    # Intent,
    # Intents,
    # IntentsInfo,
    # Segment,
    # SentimentInfo,
    # Sentiment,
    # Sentiments,
    # SummaryInfo,
    # Topic,
    # Topics,
    # TopicsInfo,
    #### unique
    AnalyzeMetadata,
    AnalyzeResults,
    AnalyzeSummary,
)

# speak
## speak REST
from .client import (
    #### top level
    SpeakRESTOptions,
    SpeakOptions,  # backward compat
    #### common
    # TextSource,
    # BufferSource,
    # StreamSource,
    # FileSource,
    #### unique
    SpeakSource,
    SpeakRestSource,
)

from .client import (
    SpeakClient,  # backward compat
    SpeakRESTClient,
    AsyncSpeakRESTClient,
)

from .client import (
    SpeakResponse,  # backward compat
    SpeakRESTResponse,
)

## speak WebSocket
from .client import SpeakWebSocketEvents, SpeakWebSocketMessage

from .client import (
    SpeakWSOptions,
)

from .client import (
    SpeakWebSocketClient,
    AsyncSpeakWebSocketClient,
    SpeakWSClient,
    AsyncSpeakWSClient,
)

from .client import (
    #### top level
    SpeakWSMetadataResponse,
    FlushedResponse,
    ClearedResponse,
    WarningResponse,
    #### common websocket response
    # OpenResponse,
    # CloseResponse,
    # UnhandledResponse,
    # ErrorResponse,
)

# manage
from .client import ManageClient, AsyncManageClient
from .client import (
    ProjectOptions,
    KeyOptions,
    ScopeOptions,
    InviteOptions,
    UsageRequestOptions,
    UsageSummaryOptions,
    UsageFieldsOptions,
)

# manage client responses
from .client import (
    #### top level
    Message,
    ProjectsResponse,
    ModelResponse,
    ModelsResponse,
    MembersResponse,
    KeyResponse,
    KeysResponse,
    ScopesResponse,
    InvitesResponse,
    UsageRequest,
    UsageResponse,
    UsageRequestsResponse,
    UsageSummaryResponse,
    UsageFieldsResponse,
    BalancesResponse,
    #### shared
    Project,
    STTDetails,
    TTSMetadata,
    TTSDetails,
    Member,
    Key,
    Invite,
    Config,
    STTUsageDetails,
    Callback,
    TokenDetail,
    SpeechSegment,
    TTSUsageDetails,
    STTTokens,
    TTSTokens,
    UsageSummaryResults,
    Resolution,
    UsageModel,
    Balance,
)

# selfhosted
from .client import (
    OnPremClient,
    AsyncOnPremClient,
    SelfHostedClient,
    AsyncSelfHostedClient,
)


# agent
from .client import AgentWebSocketEvents

# websocket
from .client import (
    AgentWebSocketClient,
    AsyncAgentWebSocketClient,
)

from .client import (
    #### common websocket response
    # OpenResponse,
    # CloseResponse,
    # ErrorResponse,
    # UnhandledResponse,
    #### unique
    WelcomeResponse,
    SettingsAppliedResponse,
    ConversationTextResponse,
    UserStartedSpeakingResponse,
    AgentThinkingResponse,
    FunctionCalling,
    FunctionCallRequest,
    AgentStartedSpeakingResponse,
    AgentAudioDoneResponse,
    InjectionRefusedResponse,
)

from .client import (
    # top level
    SettingsConfigurationOptions,
    UpdateInstructionsOptions,
    UpdateSpeakOptions,
    InjectAgentMessageOptions,
    FunctionCallResponse,
    AgentKeepAlive,
    # sub level
    Listen,
    Speak,
    Header,
    Item,
    Properties,
    Parameters,
    Function,
    Provider,
    Think,
    Agent,
    Input,
    Output,
    Audio,
    Context,
)

# utilities
# pylint: disable=wrong-import-position
from .audio import Microphone, DeepgramMicrophoneError
from .audio import (
    INPUT_LOGGING,
    INPUT_CHANNELS,
    INPUT_RATE,
    INPUT_CHUNK,
)

LOGGING = INPUT_LOGGING
CHANNELS = INPUT_CHANNELS
RATE = INPUT_RATE
CHUNK = INPUT_CHUNK

from .audio import Speaker
from .audio import (
    OUTPUT_LOGGING,
    OUTPUT_CHANNELS,
    OUTPUT_RATE,
    OUTPUT_CHUNK,
)

# pylint: enable=wrong-import-position


================================================
File: deepgram/client.py
================================================
# Copyright 2023-2024 Deepgram SDK contributors. All Rights Reserved.
# Use of this source code is governed by a MIT license that can be found in the LICENSE file.
# SPDX-License-Identifier: MIT

from typing import Optional
from importlib import import_module
import os
import logging
import deprecation  # type: ignore

from . import __version__
from .utils import verboselogs

# common
# pylint: disable=unused-import
from .clients import (
    TextSource,
    BufferSource,
    StreamSource,
    FileSource,
    UrlSource,
)
from .clients import BaseResponse
from .clients import (
    Average,
    Intent,
    Intents,
    IntentsInfo,
    Segment,
    SentimentInfo,
    Sentiment,
    Sentiments,
    SummaryInfo,
    Topic,
    Topics,
    TopicsInfo,
)
from .clients import (
    ModelInfo,
    Hit,
    Search,
)
from .clients import (
    OpenResponse,
    CloseResponse,
    UnhandledResponse,
    ErrorResponse,
)
from .clients import (
    DeepgramError,
    DeepgramTypeError,
    DeepgramModuleError,
    DeepgramApiError,
    DeepgramUnknownApiError,
)

# listen client
from .clients import ListenRouter, ReadRouter, SpeakRouter, AgentRouter

# speech-to-text
from .clients import LiveClient, AsyncLiveClient  # backward compat
from .clients import (
    ListenWebSocketClient,
    AsyncListenWebSocketClient,
)
from .clients import (
    ListenWebSocketOptions,
    LiveOptions,
    LiveTranscriptionEvents,
)

# live client responses
from .clients import (
    #### top level
    LiveResultResponse,
    ListenWSMetadataResponse,
    SpeechStartedResponse,
    UtteranceEndResponse,
    #### common websocket response
    # OpenResponse,
    # CloseResponse,
    # ErrorResponse,
    # UnhandledResponse,
    #### unique
    ListenWSMetadata,
    ListenWSAlternative,
    ListenWSChannel,
    ListenWSWord,
)

# prerecorded
from .clients import (
    # common
    # UrlSource,
    # BufferSource,
    # StreamSource,
    # TextSource,
    # FileSource,
    # unique
    PreRecordedStreamSource,
    PrerecordedSource,
    ListenRestSource,
)

from .clients import (
    PreRecordedClient,
    AsyncPreRecordedClient,
)  # backward compat
from .clients import (
    ListenRESTClient,
    AsyncListenRESTClient,
)
from .clients import (
    ListenRESTOptions,
    PrerecordedOptions,
)

# rest client responses
from .clients import (
    #### top level
    AsyncPrerecordedResponse,
    PrerecordedResponse,
    SyncPrerecordedResponse,
    #### shared
    # Average,
    # Intent,
    # Intents,
    # IntentsInfo,
    # Segment,
    # SentimentInfo,
    # Sentiment,
    # Sentiments,
    # SummaryInfo,
    # Topic,
    # Topics,
    # TopicsInfo,
    #### between rest and websocket
    # ModelInfo,
    # Alternative,
    # Hit,
    # Search,
    # Channel,
    # Word,
    # unique
    Entity,
    ListenRESTMetadata,
    Paragraph,
    Paragraphs,
    ListenRESTResults,
    Sentence,
    Summaries,
    SummaryV1,
    SummaryV2,
    Translation,
    Utterance,
    Warning,
    ListenRESTAlternative,
    ListenRESTChannel,
    ListenRESTWord,
)

# read
from .clients import ReadClient, AsyncReadClient
from .clients import AnalyzeClient, AsyncAnalyzeClient
from .clients import (
    AnalyzeOptions,
    AnalyzeStreamSource,
    AnalyzeSource,
)

# read client responses
from .clients import (
    #### top level
    AsyncAnalyzeResponse,
    SyncAnalyzeResponse,
    AnalyzeResponse,
    #### shared
    # Average,
    # Intent,
    # Intents,
    # IntentsInfo,
    # Segment,
    # SentimentInfo,
    # Sentiment,
    # Sentiments,
    # SummaryInfo,
    # Topic,
    # Topics,
    # TopicsInfo,
    #### unique
    AnalyzeMetadata,
    AnalyzeResults,
    AnalyzeSummary,
)

# speak
## speak REST
from .clients import (
    #### top level
    SpeakRESTOptions,
    SpeakOptions,  # backward compat
    #### common
    # TextSource,
    # BufferSource,
    # StreamSource,
    # FileSource,
    #### unique
    SpeakSource,
    SpeakRestSource,
    SpeakRESTSource,
)

from .clients import (
    SpeakClient,  # backward compat
    SpeakRESTClient,
    AsyncSpeakRESTClient,
)

from .clients import (
    SpeakResponse,  # backward compat
    SpeakRESTResponse,
)

## speak WebSocket
from .clients import SpeakWebSocketEvents, SpeakWebSocketMessage

from .clients import (
    SpeakWSOptions,
)

from .clients import (
    SpeakWebSocketClient,
    AsyncSpeakWebSocketClient,
    SpeakWSClient,
    AsyncSpeakWSClient,
)

from .clients import (
    #### top level
    SpeakWSMetadataResponse,
    FlushedResponse,
    ClearedResponse,
    WarningResponse,
    #### common websocket response
    # OpenResponse,
    # CloseResponse,
    # UnhandledResponse,
    # ErrorResponse,
)

# manage client classes/input
from .clients import ManageClient, AsyncManageClient
from .clients import (
    ProjectOptions,
    KeyOptions,
    ScopeOptions,
    InviteOptions,
    UsageRequestOptions,
    UsageSummaryOptions,
    UsageFieldsOptions,
)

# manage client responses
from .clients import (
    #### top level
    Message,
    ProjectsResponse,
    ModelResponse,
    ModelsResponse,
    MembersResponse,
    KeyResponse,
    KeysResponse,
    ScopesResponse,
    InvitesResponse,
    UsageRequest,
    UsageResponse,
    UsageRequestsResponse,
    UsageSummaryResponse,
    UsageFieldsResponse,
    BalancesResponse,
    #### shared
    Project,
    STTDetails,
    TTSMetadata,
    TTSDetails,
    Member,
    Key,
    Invite,
    Config,
    STTUsageDetails,
    Callback,
    TokenDetail,
    SpeechSegment,
    TTSUsageDetails,
    STTTokens,
    TTSTokens,
    UsageSummaryResults,
    Resolution,
    UsageModel,
    Balance,
)

# on-prem
from .clients import (
    OnPremClient,
    AsyncOnPremClient,
    SelfHostedClient,
    AsyncSelfHostedClient,
)


# agent
from .clients import AgentWebSocketEvents

# websocket
from .clients import (
    AgentWebSocketClient,
    AsyncAgentWebSocketClient,
)

from .clients import (
    #### common websocket response
    # OpenResponse,
    # CloseResponse,
    # ErrorResponse,
    # UnhandledResponse,
    #### unique
    WelcomeResponse,
    SettingsAppliedResponse,
    ConversationTextResponse,
    UserStartedSpeakingResponse,
    AgentThinkingResponse,
    FunctionCalling,
    FunctionCallRequest,
    AgentStartedSpeakingResponse,
    AgentAudioDoneResponse,
    InjectionRefusedResponse,
)

from .clients import (
    # top level
    SettingsConfigurationOptions,
    UpdateInstructionsOptions,
    UpdateSpeakOptions,
    InjectAgentMessageOptions,
    FunctionCallResponse,
    AgentKeepAlive,
    # sub level
    Listen,
    Speak,
    Header,
    Item,
    Properties,
    Parameters,
    Function,
    Provider,
    Think,
    Agent,
    Input,
    Output,
    Audio,
    Context,
)


# client errors and options
from .options import DeepgramClientOptions, ClientOptionsFromEnv
from .errors import DeepgramApiKeyError

# pylint: enable=unused-import


class Deepgram:  # pylint: disable=broad-exception-raised
    """
    The Deepgram class is no longer a class in version 3 of this SDK.
    """

    def __init__(self, *anything):
        raise Exception(
            """
            FATAL ERROR:
            You are attempting to instantiate a Deepgram object, which is no longer a class in version 3 of this SDK.

            To fix this issue:
                1. You need to revert to the previous version 2 of the SDK: pip install deepgram-sdk==2.12.0
                2. or, update your application's code to use version 3 of this SDK. See the README for more information.

            Things to consider:

                - This Version 3 of the SDK requires Python 3.10 or higher.
                  Older versions (3.9 and lower) of Python are nearing end-of-life: https://devguide.python.org/versions/
                  Understand the risks of using a version of Python nearing EOL.

                - Version 2 of the SDK will receive maintenance updates in the form of security fixes only.
                  No new features will be added to version 2 of the SDK.
            """
        )


class DeepgramClient:
    """
    Represents a client for interacting with the Deepgram API.

    This class provides a client for making requests to the Deepgram API with various configuration options.

    Attributes:
        api_key (str): The Deepgram API key used for authentication.
        config_options (DeepgramClientOptions): An optional configuration object specifying client options.

    Raises:
        DeepgramApiKeyError: If the API key is missing or invalid.

    Methods:
        listen: Returns a ListenClient instance for interacting with Deepgram's transcription services.

        manage: (Preferred) Returns a Threaded ManageClient instance for managing Deepgram resources.
        selfhosted: (Preferred) Returns an Threaded SelfHostedClient instance for interacting with Deepgram's on-premises API.

        asyncmanage: Returns an (Async) ManageClient instance for managing Deepgram resources.
        asyncselfhosted: Returns an (Async) SelfHostedClient instance for interacting with Deepgram's on-premises API.
    """

    _config: DeepgramClientOptions
    _logger: verboselogs.VerboseLogger

    def __init__(
        self,
        api_key: str = "",
        config: Optional[DeepgramClientOptions] = None,
    ):
        self._logger = verboselogs.VerboseLogger(__name__)
        self._logger.addHandler(logging.StreamHandler())

        if api_key == "" and config is not None:
            self._logger.info("Attempting to set API key from config object")
            api_key = config.api_key
        if api_key == "":
            self._logger.info("Attempting to set API key from environment variable")
            api_key = os.getenv("DEEPGRAM_API_KEY", "")
        if api_key == "":
            self._logger.warning("WARNING: API key is missing")

        self.api_key = api_key
        if config is None:  # Use default configuration
            self._config = DeepgramClientOptions(self.api_key)
        else:
            config.set_apikey(self.api_key)
            self._config = config

    @property
    def listen(self):
        """
        Returns a Listen dot-notation router for interacting with Deepgram's transcription services.
        """
        return ListenRouter(self._config)

    @property
    def read(self):
        """
        Returns a Read dot-notation router for interacting with Deepgram's read services.
        """
        return ReadRouter(self._config)

    @property
    def speak(self):
        """
        Returns a Speak dot-notation router for interacting with Deepgram's speak services.
        """
        return SpeakRouter(self._config)

    @property
    @deprecation.deprecated(
        deprecated_in="3.4.0",
        removed_in="4.0.0",
        current_version=__version__,
        details="deepgram.asyncspeak is deprecated. Use deepgram.speak.asyncrest instead.",
    )
    def asyncspeak(self):
        """
        DEPRECATED: deepgram.asyncspeak is deprecated. Use deepgram.speak.asyncrest instead.
        """
        return self.Version(self._config, "asyncspeak")

    @property
    def manage(self):
        """
        Returns a ManageClient instance for managing Deepgram resources.
        """
        return self.Version(self._config, "manage")

    @property
    def asyncmanage(self):
        """
        Returns an AsyncManageClient instance for managing Deepgram resources.
        """
        return self.Version(self._config, "asyncmanage")

    @property
    @deprecation.deprecated(
        deprecated_in="3.4.0",
        removed_in="4.0.0",
        current_version=__version__,
        details="deepgram.onprem is deprecated. Use deepgram.speak.selfhosted instead.",
    )
    def onprem(self):
        """
        DEPRECATED: deepgram.onprem is deprecated. Use deepgram.speak.selfhosted instead.
        """
        return self.Version(self._config, "selfhosted")

    @property
    def selfhosted(self):
        """
        Returns an SelfHostedClient instance for interacting with Deepgram's on-premises API.
        """
        return self.Version(self._config, "selfhosted")

    @property
    @deprecation.deprecated(
        deprecated_in="3.4.0",
        removed_in="4.0.0",
        current_version=__version__,
        details="deepgram.asynconprem is deprecated. Use deepgram.speak.asyncselfhosted instead.",
    )
    def asynconprem(self):
        """
        DEPRECATED: deepgram.asynconprem is deprecated. Use deepgram.speak.asyncselfhosted instead.
        """
        return self.Version(self._config, "asyncselfhosted")

    @property
    def asyncselfhosted(self):
        """
        Returns an AsyncSelfHostedClient instance for interacting with Deepgram's on-premises API.
        """
        return self.Version(self._config, "asyncselfhosted")

    @property
    def agent(self):
        """
        Returns a Agent dot-notation router for interacting with Deepgram's speak services.
        """
        return AgentRouter(self._config)

    # INTERNAL CLASSES
    class Version:
        """
        Represents a version of the Deepgram API.
        """

        _logger: verboselogs.VerboseLogger
        _config: DeepgramClientOptions
        _parent: str

        def __init__(self, config, parent: str):
            self._logger = verboselogs.VerboseLogger(__name__)
            self._logger.addHandler(logging.StreamHandler())
            self._logger.setLevel(config.verbose)

            self._config = config
            self._parent = parent

        # FUTURE VERSIONING:
        # When v2 or v1.1beta1 or etc. This allows easy access to the latest version of the API.
        # @property
        # def latest(self):
        #     match self._parent:
        #         case "manage":
        #             return ManageClient(self._config)
        #         case "selfhosted":
        #             return SelfHostedClient(self._config)
        #         case _:
        #             raise DeepgramModuleError("Invalid parent")

        def v(self, version: str = ""):
            # pylint: disable-msg=too-many-statements
            """
            Returns a client for the specified version of the API.
            """
            self._logger.debug("Version.v ENTER")
            self._logger.info("version: %s", version)
            if len(version) == 0:
                self._logger.error("version is empty")
                self._logger.debug("Version.v LEAVE")
                raise DeepgramModuleError("Invalid module version")

            parent = ""
            filename = ""
            classname = ""
            match self._parent:
                case "manage":
                    parent = "manage"
                    filename = "client"
                    classname = "ManageClient"
                case "asyncmanage":
                    parent = "manage"
                    filename = "async_client"
                    classname = "AsyncManageClient"
                case "asyncspeak":
                    return AsyncSpeakRESTClient(self._config)
                case "selfhosted":
                    parent = "selfhosted"
                    filename = "client"
                    classname = "SelfHostedClient"
                case "asyncselfhosted":
                    parent = "selfhosted"
                    filename = "async_client"
                    classname = "AsyncSelfHostedClient"
                case _:
                    self._logger.error("parent unknown: %s", self._parent)
                    self._logger.debug("Version.v LEAVE")
                    raise DeepgramModuleError("Invalid parent type")

            # create class path
            path = f"deepgram.clients.{parent}.v{version}.{filename}"
            self._logger.info("path: %s", path)
            self._logger.info("classname: %s", classname)

            # import class
            mod = import_module(path)
            if mod is None:
                self._logger.error("module path is None")
                self._logger.debug("Version.v LEAVE")
                raise DeepgramModuleError("Unable to find package")

            my_class = getattr(mod, classname)
            if my_class is None:
                self._logger.error("my_class is None")
                self._logger.debug("Version.v LEAVE")
                raise DeepgramModuleError("Unable to find class")

            # instantiate class
            my_class_instance = my_class(self._config)
            self._logger.notice("Version.v succeeded")
            self._logger.debug("Version.v LEAVE")
            return my_class_instance

        # pylint: enable-msg=too-many-statements


================================================
File: deepgram/errors.py
================================================
# Copyright 2023-2024 Deepgram SDK contributors. All Rights Reserved.
# Use of this source code is governed by a MIT license that can be found in the LICENSE file.
# SPDX-License-Identifier: MIT


class DeepgramApiKeyError(Exception):
    """
    Base class for exceptions raised for a missing Deepgram API Key.

    Attributes:
        message (str): The error message describing the exception.
    """

    def __init__(self, message: str):
        super().__init__(message)
        self.name = "DeepgramApiKeyError"


================================================
File: deepgram/options.py
================================================
# Copyright 2023-2024 Deepgram SDK contributors. All Rights Reserved.
# Use of this source code is governed by a MIT license that can be found in the LICENSE file.
# SPDX-License-Identifier: MIT

import sys
import re
import os
from typing import Dict, Optional
import logging
import numbers

from deepgram import __version__
from .utils import verboselogs
from .errors import DeepgramApiKeyError


class DeepgramClientOptions:  # pylint: disable=too-many-instance-attributes
    """
    Represents options for configuring a Deepgram client.

    This class allows you to customize various options for interacting with the Deepgram API.

    Attributes:
        api_key: (Optional) A Deepgram API key used for authentication. Default uses the `DEEPGRAM_API_KEY` environment variable.
        url: (Optional) The URL used to interact with production, On-prem, and other Deepgram environments. Defaults to `api.deepgram.com`.
        verbose: (Optional) The logging level for the client. Defaults to `verboselogs.WARNING`.
        headers: (Optional) Headers for initializing the client.
        options: (Optional) Additional options for initializing the client.
    """

    _logger: verboselogs.VerboseLogger
    _inspect_listen: bool = False
    _inspect_speak: bool = False

    def __init__(
        self,
        api_key: str = "",
        url: str = "",
        verbose: int = verboselogs.WARNING,
        headers: Optional[Dict] = None,
        options: Optional[Dict] = None,
    ):  # pylint: disable=too-many-positional-arguments
        self._logger = verboselogs.VerboseLogger(__name__)
        self._logger.addHandler(logging.StreamHandler())

        if api_key is None:
            api_key = ""

        self.verbose = verbose
        self.api_key = api_key

        if headers is None:
            headers = {}
        self._update_headers(headers=headers)

        if len(url) == 0:
            url = "api.deepgram.com"
        self.url = self._get_url(url)

        if options is None:
            options = {}
        self.options = options

        if self.is_auto_flush_reply_enabled():
            self._inspect_listen = True
        if self.is_auto_flush_speak_enabled():
            self._inspect_speak = True

    def set_apikey(self, api_key: str):
        """
        set_apikey: Sets the API key for the client.

        Args:
            api_key: The Deepgram API key used for authentication.
        """
        self.api_key = api_key
        self._update_headers()

    def _get_url(self, url) -> str:
        if not re.match(r"^https?://", url, re.IGNORECASE):
            url = "https://" + url
        return url.strip("/")

    def _update_headers(self, headers: Optional[Dict] = None):
        self.headers = {}
        self.headers["Accept"] = "application/json"
        if self.api_key:
            self.headers["Authorization"] = f"Token {self.api_key}"
        elif "Authorization" in self.headers:
            del self.headers["Authorization"]
        self.headers[
            "User-Agent"
        ] = f"@deepgram/sdk/{__version__} python/{sys.version_info[1]}.{sys.version_info[2]}"
        # Overwrite / add any headers that were passed in
        if headers:
            self.headers.update(headers)

    def is_keep_alive_enabled(self) -> bool:
        """
        is_keep_alive_enabled: Returns True if the client is configured to keep the connection alive.
        """
        return self.options.get("keepalive", False) or self.options.get(
            "keep_alive", False
        )

    def is_auto_flush_reply_enabled(self) -> bool:
        """
        is_auto_flush_reply_enabled: Returns True if the client is configured to auto-flush for listen.
        """
        auto_flush_reply_delta = float(self.options.get("auto_flush_reply_delta", 0))
        return (
            isinstance(auto_flush_reply_delta, numbers.Number)
            and auto_flush_reply_delta > 0
        )

    def is_auto_flush_speak_enabled(self) -> bool:
        """
        is_auto_flush_speak_enabled: Returns True if the client is configured to auto-flush for speak.
        """
        auto_flush_speak_delta = float(self.options.get("auto_flush_speak_delta", 0))
        return (
            isinstance(auto_flush_speak_delta, numbers.Number)
            and auto_flush_speak_delta > 0
        )

    def is_inspecting_listen(self) -> bool:
        """
        is_inspecting_listen: Returns True if the client is inspecting listen messages.
        """
        return self._inspect_listen

    def is_inspecting_speak(self) -> bool:
        """
        is_inspecting_speak: Returns True if the client is inspecting speak messages.
        """
        return self._inspect_speak


class ClientOptionsFromEnv(
    DeepgramClientOptions
):  # pylint: disable=too-many-branches, too-many-statements
    """
    This class extends DeepgramClientOptions and will attempt to use environment variables first before defaults.
    """

    _logger: verboselogs.VerboseLogger

    def __init__(
        self,
        api_key: str = "",
        url: str = "",
        verbose: int = verboselogs.WARNING,
        headers: Optional[Dict] = None,
        options: Optional[Dict] = None,
    ):  # pylint: disable=too-many-positional-arguments
        self._logger = verboselogs.VerboseLogger(__name__)
        self._logger.addHandler(logging.StreamHandler())
        self._logger.setLevel(verboselogs.WARNING)  # temporary set for setup

        if api_key is None:
            api_key = ""

        if api_key == "":
            api_key = os.getenv("DEEPGRAM_API_KEY", "")
            if api_key == "":
                self._logger.critical("Deepgram API KEY is not set")
                raise DeepgramApiKeyError("Deepgram API KEY is not set")

        if url == "":
            url = os.getenv("DEEPGRAM_HOST", "api.deepgram.com")
            self._logger.notice(f"Deepgram host is set to {url}")

        if verbose == verboselogs.WARNING:
            _loglevel = os.getenv("DEEPGRAM_LOGGING", "")
            if _loglevel != "":
                verbose = int(_loglevel)
            if isinstance(verbose, str):
                match verbose:
                    case "NOTSET":
                        self._logger.notice("Logging level is set to NOTSET")
                        verbose = verboselogs.NOTSET
                    case "SPAM":
                        self._logger.notice("Logging level is set to SPAM")
                        verbose = verboselogs.SPAM
                    case "DEBUG":
                        self._logger.notice("Logging level is set to DEBUG")
                        verbose = verboselogs.DEBUG
                    case "VERBOSE":
                        self._logger.notice("Logging level is set to VERBOSE")
                        verbose = verboselogs.VERBOSE
                    case "NOTICE":
                        self._logger.notice("Logging level is set to NOTICE")
                        verbose = verboselogs.NOTICE
                    case "WARNING":
                        self._logger.notice("Logging level is set to WARNING")
                        verbose = verboselogs.WARNING
                    case "SUCCESS":
                        self._logger.notice("Logging level is set to SUCCESS")
                        verbose = verboselogs.SUCCESS
                    case "ERROR":
                        self._logger.notice("Logging level is set to ERROR")
                        verbose = verboselogs.ERROR
                    case "CRITICAL":
                        self._logger.notice("Logging level is set to CRITICAL")
                        verbose = verboselogs.CRITICAL
                    case _:
                        self._logger.notice("Logging level is set to WARNING")
                        verbose = verboselogs.WARNING
        self._logger.notice(f"Logging level is set to {verbose}")

        if headers is None:
            headers = {}
            for x in range(0, 20):
                header = os.getenv(f"DEEPGRAM_HEADER_{x}", None)
                if header is not None:
                    headers[header] = os.getenv(f"DEEPGRAM_HEADER_VALUE_{x}", None)
                    self._logger.debug(
                        "Deepgram header %s is set with value %s",
                        header,
                        headers[header],
                    )
                else:
                    break
            if len(headers) == 0:
                self._logger.notice("Deepgram headers are not set")
                headers = None

        if options is None:
            options = {}
            for x in range(0, 20):
                param = os.getenv(f"DEEPGRAM_PARAM_{x}", None)
                if param is not None:
                    options[param] = os.getenv(f"DEEPGRAM_PARAM_VALUE_{x}", None)
                    self._logger.debug(
                        "Deepgram option %s is set with value %s", param, options[param]
                    )
                else:
                    break
            if len(options) == 0:
                self._logger.notice("Deepgram options are not set")
                options = None

        super().__init__(
            api_key=api_key, url=url, verbose=verbose, headers=headers, options=options
        )


================================================
File: deepgram/audio/__init__.py
================================================
# Copyright 2023-2024 Deepgram SDK contributors. All Rights Reserved.
# Use of this source code is governed by a MIT license that can be found in the LICENSE file.
# SPDX-License-Identifier: MIT

from .microphone import Microphone
from .microphone import DeepgramMicrophoneError
from .microphone import (
    LOGGING as INPUT_LOGGING,
    CHANNELS as INPUT_CHANNELS,
    RATE as INPUT_RATE,
    CHUNK as INPUT_CHUNK,
)

from .speaker import Speaker
from .speaker import DeepgramSpeakerError
from .speaker import (
    LOGGING as OUTPUT_LOGGING,
    CHANNELS as OUTPUT_CHANNELS,
    RATE as OUTPUT_RATE,
    CHUNK as OUTPUT_CHUNK,
    PLAYBACK_DELTA as OUTPUT_PLAYBACK_DELTA,
)


================================================
File: deepgram/audio/microphone/__init__.py
================================================
# Copyright 2023-2024 Deepgram SDK contributors. All Rights Reserved.
# Use of this source code is governed by a MIT license that can be found in the LICENSE file.
# SPDX-License-Identifier: MIT

from .microphone import Microphone
from .constants import LOGGING, CHANNELS, RATE, CHUNK
from .errors import DeepgramMicrophoneError


================================================
File: deepgram/audio/microphone/constants.py
================================================
# Copyright 2023-2024 Deepgram SDK contributors. All Rights Reserved.
# Use of this source code is governed by a MIT license that can be found in the LICENSE file.
# SPDX-License-Identifier: MIT

from ...utils import verboselogs

# Constants for microphone
LOGGING = verboselogs.WARNING
CHANNELS = 1
RATE = 16000
CHUNK = 8194


================================================
File: deepgram/audio/microphone/errors.py
================================================
# Copyright 2023-2024 Deepgram SDK contributors. All Rights Reserved.
# Use of this source code is governed by a MIT license that can be found in the LICENSE file.
# SPDX-License-Identifier: MIT


# exceptions for microphone
class DeepgramMicrophoneError(Exception):
    """
    Exception raised for known errors related to Microphone library.

    Attributes:
        message (str): The error message describing the exception.
    """

    def __init__(self, message: str):
        super().__init__(message)
        self.name = "DeepgramMicrophoneError"
        self.message = message

    def __str__(self):
        return f"{self.name}: {self.message}"


================================================
File: deepgram/audio/microphone/microphone.py
================================================
# Copyright 2023-2024 Deepgram SDK contributors. All Rights Reserved.
# Use of this source code is governed by a MIT license that can be found in the LICENSE file.
# SPDX-License-Identifier: MIT

import inspect
import asyncio
import threading
from typing import Optional, Callable, Union, TYPE_CHECKING
import logging

from ...utils import verboselogs

from .constants import LOGGING, CHANNELS, RATE, CHUNK

if TYPE_CHECKING:
    import pyaudio


class Microphone:  # pylint: disable=too-many-instance-attributes
    """
    This implements a microphone for local audio input. This uses PyAudio under the hood.
    """

    _logger: verboselogs.VerboseLogger

    _audio: Optional["pyaudio.PyAudio"] = None
    _stream: Optional["pyaudio.Stream"] = None

    _chunk: int
    _rate: int
    _format: int
    _channels: int
    _input_device_index: Optional[int]
    _is_muted: bool

    _asyncio_loop: asyncio.AbstractEventLoop
    _asyncio_thread: Optional[threading.Thread] = None
    _exit: threading.Event

    _push_callback_org: Optional[Callable] = None
    _push_callback: Optional[Callable] = None

    def __init__(
        self,
        push_callback: Optional[Callable] = None,
        verbose: int = LOGGING,
        rate: int = RATE,
        chunk: int = CHUNK,
        channels: int = CHANNELS,
        input_device_index: Optional[int] = None,
    ):  # pylint: disable=too-many-positional-arguments
        # dynamic import of pyaudio as not to force the requirements on the SDK (and users)
        import pyaudio  # pylint: disable=import-outside-toplevel

        self._logger = verboselogs.VerboseLogger(__name__)
        self._logger.addHandler(logging.StreamHandler())
        self._logger.setLevel(verbose)

        self._exit = threading.Event()

        self._audio = pyaudio.PyAudio()
        self._chunk = chunk
        self._rate = rate
        self._format = pyaudio.paInt16
        self._channels = channels
        self._is_muted = False

        self._input_device_index = input_device_index
        self._push_callback_org = push_callback

    def _start_asyncio_loop(self) -> None:
        self._asyncio_loop = asyncio.new_event_loop()
        self._asyncio_loop.run_forever()

    def is_active(self) -> bool:
        """
        is_active - returns the state of the stream

        Args:
            None

        Returns:
            True if the stream is active, False otherwise
        """
        self._logger.debug("Microphone.is_active ENTER")

        if self._stream is None:
            self._logger.error("stream is None")
            self._logger.debug("Microphone.is_active LEAVE")
            return False

        val = self._stream.is_active()
        self._logger.info("is_active: %s", val)
        self._logger.info("is_exiting: %s", self._exit.is_set())
        self._logger.debug("Microphone.is_active LEAVE")
        return val

    def set_callback(self, push_callback: Callable) -> None:
        """
        set_callback - sets the callback function to be called when data is received.

        Args:
            push_callback (Callable): The callback function to be called when data is received.
                                      This should be the websocket send function.

        Returns:
            None
        """
        self._push_callback_org = push_callback

    def start(self) -> bool:
        """
        starts - starts the microphone stream

        Returns:
            bool: True if the stream was started, False otherwise
        """
        self._logger.debug("Microphone.start ENTER")

        self._logger.info("format: %s", self._format)
        self._logger.info("channels: %d", self._channels)
        self._logger.info("rate: %d", self._rate)
        self._logger.info("chunk: %d", self._chunk)
        # self._logger.info("input_device_id: %d", self._input_device_index)

        if self._push_callback_org is None:
            self._logger.error("start failed. No callback set.")
            self._logger.debug("Microphone.start LEAVE")
            return False

        if inspect.iscoroutinefunction(self._push_callback_org):
            self._logger.verbose("async/await callback - wrapping")
            # Run our own asyncio loop.
            self._asyncio_thread = threading.Thread(target=self._start_asyncio_loop)
            self._asyncio_thread.start()

            self._push_callback = lambda data: (
                asyncio.run_coroutine_threadsafe(
                    self._push_callback_org(data), self._asyncio_loop
                ).result()
                if self._push_callback_org
                else None
            )
        else:
            self._logger.verbose("regular threaded callback")
            self._asyncio_thread = None
            self._push_callback = self._push_callback_org

        if self._audio is not None:
            self._stream = self._audio.open(
                format=self._format,
                channels=self._channels,
                rate=self._rate,
                input=True,
                output=False,
                frames_per_buffer=self._chunk,
                input_device_index=self._input_device_index,
                stream_callback=self._callback,
            )

        if self._stream is None:
            self._logger.error("start failed. No stream created.")
            self._logger.debug("Microphone.start LEAVE")
            return False

        self._exit.clear()
        if self._stream is not None:
            self._stream.start_stream()

        self._logger.notice("start succeeded")
        self._logger.debug("Microphone.start LEAVE")
        return True

    def mute(self) -> bool:
        """
        mute - mutes the microphone stream

        Returns:
            bool: True if the stream was muted, False otherwise
        """
        self._logger.verbose("Microphone.mute ENTER")

        if self._stream is None:
            self._logger.error("mute failed. Library not initialized.")
            self._logger.verbose("Microphone.mute LEAVE")
            return False

        self._is_muted = True

        self._logger.notice("mute succeeded")
        self._logger.verbose("Microphone.mute LEAVE")
        return True

    def unmute(self) -> bool:
        """
        unmute - unmutes the microphone stream

        Returns:
            bool: True if the stream was unmuted, False otherwise
        """
        self._logger.verbose("Microphone.unmute ENTER")

        if self._stream is None:
            self._logger.error("unmute failed. Library not initialized.")
            self._logger.verbose("Microphone.unmute LEAVE")
            return False

        self._is_muted = False

        self._logger.notice("unmute succeeded")
        self._logger.verbose("Microphone.unmute LEAVE")
        return True

    def is_muted(self) -> bool:
        """
        is_muted - returns the state of the stream

        Args:
            None

        Returns:
            True if the stream is muted, False otherwise
        """
        self._logger.spam("Microphone.is_muted ENTER")

        if self._stream is None:
            self._logger.spam("is_muted: stream is None")
            self._logger.spam("Microphone.is_muted LEAVE")
            return False

        val = self._is_muted

        self._logger.spam("is_muted: %s", val)
        self._logger.spam("Microphone.is_muted LEAVE")
        return val

    def finish(self) -> bool:
        """
        finish - stops the microphone stream

        Returns:
            bool: True if the stream was stopped, False otherwise
        """
        self._logger.debug("Microphone.finish ENTER")

        self._logger.notice("signal exit")
        self._exit.set()

        # Stop the stream.
        if self._stream is not None:
            self._logger.notice("stopping stream...")
            self._stream.stop_stream()
            self._stream.close()
            self._logger.notice("stream stopped")

        # clean up the thread
        if (
            # inspect.iscoroutinefunction(self._push_callback_org)
            # and
            self._asyncio_thread
            is not None
        ):
            self._logger.notice("stopping _asyncio_loop...")
            self._asyncio_loop.call_soon_threadsafe(self._asyncio_loop.stop)
            self._asyncio_thread.join()
            self._logger.notice("_asyncio_thread joined")
        self._stream = None
        self._asyncio_thread = None

        self._logger.notice("finish succeeded")
        self._logger.debug("Microphone.finish LEAVE")

        return True

    def _callback(
        self, input_data, frame_count, time_info, status_flags
    ):  # pylint: disable=unused-argument
        """
        The callback used to process data in callback mode.
        """
        # dynamic import of pyaudio as not to force the requirements on the SDK (and users)
        import pyaudio  # pylint: disable=import-outside-toplevel

        if self._exit.is_set():
            self._logger.notice("_callback exit is Set. stopping...")
            return None, pyaudio.paAbort

        if input_data is None:
            self._logger.warning("input_data is None")
            return None, pyaudio.paContinue

        try:
            if self._is_muted:
                size = len(input_data)
                input_data = b"\x00" * size

            self._push_callback(input_data)
        except Exception as e:
            self._logger.error("Error while sending: %s", str(e))
            raise

        return input_data, pyaudio.paContinue


================================================
File: deepgram/audio/speaker/__init__.py
================================================
# Copyright 2023-2024 Deepgram SDK contributors. All Rights Reserved.
# Use of this source code is governed by a MIT license that can be found in the LICENSE file.
# SPDX-License-Identifier: MIT

from .speaker import Speaker
from .errors import DeepgramSpeakerError
from .constants import LOGGING, CHANNELS, RATE, CHUNK, PLAYBACK_DELTA


================================================
File: deepgram/audio/speaker/constants.py
================================================
# Copyright 2024 Deepgram SDK contributors. All Rights Reserved.
# Use of this source code is governed by a MIT license that can be found in the LICENSE file.
# SPDX-License-Identifier: MIT

from ...utils import verboselogs

# Constants for speaker
LOGGING = verboselogs.WARNING
TIMEOUT = 0.050
CHANNELS = 1
RATE = 16000
CHUNK = 8194

# Constants for speaker
PLAYBACK_DELTA = 2000


================================================
File: deepgram/audio/speaker/errors.py
================================================
# Copyright 2024 Deepgram SDK contributors. All Rights Reserved.
# Use of this source code is governed by a MIT license that can be found in the LICENSE file.
# SPDX-License-Identifier: MIT


# exceptions for speaker
class DeepgramSpeakerError(Exception):
    """
    Exception raised for known errors related to Speaker library.

    Attributes:
        message (str): The error message describing the exception.
    """

    def __init__(self, message: str):
        super().__init__(message)
        self.name = "DeepgramSpeakerError"
        self.message = message

    def __str__(self):
        return f"{self.name}: {self.message}"


================================================
File: deepgram/audio/speaker/speaker.py
================================================
# Copyright 2024 Deepgram SDK contributors. All Rights Reserved.
# Use of this source code is governed by a MIT license that can be found in the LICENSE file.
# SPDX-License-Identifier: MIT

import asyncio
import inspect
import queue
import threading
from typing import Optional, Callable, Union, TYPE_CHECKING
import logging
from datetime import datetime

import websockets

from ...utils import verboselogs
from .constants import LOGGING, CHANNELS, RATE, CHUNK, TIMEOUT, PLAYBACK_DELTA

from ..microphone import Microphone

if TYPE_CHECKING:
    import pyaudio

HALF_SECOND = 0.5


class Speaker:  # pylint: disable=too-many-instance-attributes
    """
    This implements a speaker for local audio output. This uses PyAudio under the hood.
    """

    _logger: verboselogs.VerboseLogger

    _audio: Optional["pyaudio.PyAudio"] = None
    _stream: Optional["pyaudio.Stream"] = None

    _chunk: int
    _rate: int
    _channels: int
    _output_device_index: Optional[int] = None

    # last time we received audio
    _last_datagram: datetime = datetime.now()
    _last_play_delta_in_ms: int
    _lock_wait: threading.Lock

    _queue: queue.Queue
    _exit: threading.Event

    _thread: Optional[threading.Thread] = None
    # _asyncio_loop: asyncio.AbstractEventLoop
    # _asyncio_thread: threading.Thread
    _receiver_thread: Optional[threading.Thread] = None
    _loop: Optional[asyncio.AbstractEventLoop] = None

    _push_callback_org: Optional[Callable] = None
    _push_callback: Optional[Callable] = None
    _pull_callback_org: Optional[Callable] = None
    _pull_callback: Optional[Callable] = None

    _microphone: Optional[Microphone] = None

    def __init__(
        self,
        pull_callback: Optional[Callable] = None,
        push_callback: Optional[Callable] = None,
        verbose: int = LOGGING,
        rate: int = RATE,
        chunk: int = CHUNK,
        channels: int = CHANNELS,
        last_play_delta_in_ms: int = PLAYBACK_DELTA,
        output_device_index: Optional[int] = None,
        microphone: Optional[Microphone] = None,
    ):  # pylint: disable=too-many-positional-arguments
        # dynamic import of pyaudio as not to force the requirements on the SDK (and users)
        import pyaudio  # pylint: disable=import-outside-toplevel

        self._logger = verboselogs.VerboseLogger(__name__)
        self._logger.addHandler(logging.StreamHandler())
        self._logger.setLevel(verbose)

        self._exit = threading.Event()
        self._queue = queue.Queue()

        self._last_datagram = datetime.now()
        self._lock_wait = threading.Lock()

        self._microphone = microphone

        self._audio = pyaudio.PyAudio()
        self._chunk = chunk
        self._rate = rate
        self._format = pyaudio.paInt16
        self._channels = channels
        self._last_play_delta_in_ms = last_play_delta_in_ms
        self._output_device_index = output_device_index

        self._push_callback_org = push_callback
        self._pull_callback_org = pull_callback

    def set_push_callback(self, push_callback: Callable) -> None:
        """
        set_push_callback - sets the callback function to be called when data is sent.

        Args:
            push_callback (Callable): The callback function to be called when data is send.
                                      This should be the websocket handle message function.

        Returns:
            None
        """
        self._push_callback_org = push_callback

    def set_pull_callback(self, pull_callback: Callable) -> None:
        """
        set_pull_callback - sets the callback function to be called when data is received.

        Args:
            pull_callback (Callable): The callback function to be called when data is received.
                                      This should be the websocket recv function.

        Returns:
            None
        """
        self._pull_callback_org = pull_callback

    def start(self, active_loop: Optional[asyncio.AbstractEventLoop] = None) -> bool:
        """
        starts - starts the Speaker stream

        Args:
            socket (Union[SyncClientConnection, AsyncClientConnection]): The socket to receive audio data from.

        Returns:
            bool: True if the stream was started, False otherwise
        """
        self._logger.debug("Speaker.start ENTER")

        self._logger.info("format: %s", self._format)
        self._logger.info("channels: %d", self._channels)
        self._logger.info("rate: %d", self._rate)
        self._logger.info("chunk: %d", self._chunk)
        # self._logger.info("output_device_id: %d", self._output_device_index)

        # Automatically get the current running event loop
        if inspect.iscoroutinefunction(self._push_callback_org) and active_loop is None:
            self._logger.verbose("get default running asyncio loop")
            self._loop = asyncio.get_running_loop()

        self._exit.clear()
        self._queue = queue.Queue()

        if self._audio is not None:
            self._stream = self._audio.open(
                format=self._format,
                channels=self._channels,
                rate=self._rate,
                input=False,
                output=True,
                frames_per_buffer=self._chunk,
                output_device_index=self._output_device_index,
            )

        if self._stream is None:
            self._logger.error("start failed. No stream created.")
            self._logger.debug("Speaker.start LEAVE")
            return False

        self._push_callback = self._push_callback_org
        self._pull_callback = self._pull_callback_org

        # start the play thread
        self._thread = threading.Thread(
            target=self._play, args=(self._queue, self._stream, self._exit), daemon=True
        )
        self._thread.start()

        # Start the stream
        if self._stream is not None:
            self._stream.start_stream()

        # Start the receiver thread within the start function
        self._logger.verbose("Starting receiver thread...")
        self._receiver_thread = threading.Thread(target=self._start_receiver)
        self._receiver_thread.start()

        self._logger.notice("start succeeded")
        self._logger.debug("Speaker.start LEAVE")

        return True

    def wait_for_complete_with_mute(self, mic: Microphone):
        """
        This method will mute/unmute a Microphone and block until the speak is done playing sound.
        """
        self._logger.debug("Speaker.wait_for_complete ENTER")

        if self._microphone is not None:
            mic.mute()
        self.wait_for_complete()
        if self._microphone is not None:
            mic.unmute()

        self._logger.debug("Speaker.wait_for_complete LEAVE")

    def wait_for_complete(self):
        """
        This method will block until the speak is done playing sound.
        """
        self._logger.debug("Speaker.wait_for_complete ENTER")

        delta_in_ms = float(self._last_play_delta_in_ms)
        self._logger.debug("Last Play delta: %f", delta_in_ms)

        # set to now
        with self._lock_wait:
            self._last_datagram = datetime.now()

        while True:
            # sleep for a bit
            self._exit.wait(HALF_SECOND)

            # check if we should exit
            if self._exit.is_set():
                self._logger.debug("Exiting wait_for_complete _exit is set")
                break

            # check the time
            with self._lock_wait:
                delta = datetime.now() - self._last_datagram
                diff_in_ms = delta.total_seconds() * 1000
                if diff_in_ms < delta_in_ms:
                    self._logger.debug("LastPlay delta is less than threshold")
                    continue

            # if we get here, we are done playing audio
            self._logger.debug("LastPlay delta is greater than threshold. Exit wait!")
            break

        self._logger.debug("Speaker.wait_for_complete LEAVE")

    def _start_receiver(self):
        # Check if the socket is an asyncio WebSocket
        if inspect.iscoroutinefunction(self._pull_callback_org):
            self._logger.verbose("Starting asyncio receiver...")
            asyncio.run_coroutine_threadsafe(self._start_asyncio_receiver(), self._loop)
        else:
            self._logger.verbose("Starting threaded receiver...")
            self._start_threaded_receiver()

    async def _start_asyncio_receiver(self):
        try:
            while True:
                if self._exit.is_set():
                    self._logger.verbose("Exiting receiver thread...")
                    break

                message = await self._pull_callback()
                if message is None:
                    self._logger.verbose("No message received...")
                    continue

                if isinstance(message, str):
                    self._logger.verbose("Received control message...")
                    await self._push_callback(message)
                elif isinstance(message, bytes):
                    self._logger.verbose("Received audio data...")
                    await self._push_callback(message)
                    self.add_audio_to_queue(message)
        except websockets.exceptions.ConnectionClosedOK as e:
            self._logger.debug("send() exiting gracefully: %d", e.code)
        except websockets.exceptions.ConnectionClosed as e:
            if e.code in [1000, 1001]:
                self._logger.debug("send() exiting gracefully: %d", e.code)
                return
            self._logger.error("_start_asyncio_receiver - ConnectionClosed: %s", str(e))
        except websockets.exceptions.WebSocketException as e:
            self._logger.error(
                "_start_asyncio_receiver- WebSocketException: %s", str(e)
            )
        except Exception as e:  # pylint: disable=broad-except
            self._logger.error("_start_asyncio_receiver exception: %s", str(e))

    def _start_threaded_receiver(self):
        try:
            while True:
                if self._exit.is_set():
                    self._logger.verbose("Exiting receiver thread...")
                    break

                message = self._pull_callback()
                if message is None:
                    self._logger.verbose("No message received...")
                    continue

                if isinstance(message, str):
                    self._logger.verbose("Received control message...")
                    self._push_callback(message)
                elif isinstance(message, bytes):
                    self._logger.verbose("Received audio data...")
                    self._push_callback(message)
                    self.add_audio_to_queue(message)
        except Exception as e:  # pylint: disable=broad-except
            self._logger.notice("_start_threaded_receiver exception: %s", str(e))

    def add_audio_to_queue(self, data: bytes) -> None:
        """
        add_audio_to_queue - adds audio data to the Speaker queue

        Args:
            data (bytes): The audio data to add to the queue
        """
        self._queue.put(data)

    def finish(self) -> bool:
        """
        finish - stops the Speaker stream

        Returns:
            bool: True if the stream was stopped, False otherwise
        """
        self._logger.debug("Speaker.finish ENTER")

        self._logger.notice("signal exit")
        self._exit.set()

        if self._stream is not None:
            self._logger.notice("stopping stream...")
            self._stream.stop_stream()
            self._stream.close()
            self._logger.notice("stream stopped")

        if self._thread is not None:
            self._logger.notice("joining _thread...")
            self._thread.join()
            self._logger.notice("thread stopped")

        if self._receiver_thread is not None:
            self._logger.notice("stopping _receiver_thread...")
            self._receiver_thread.join()
            self._logger.notice("_receiver_thread joined")

        with self._queue.mutex:
            self._queue.queue.clear()

        self._stream = None
        self._thread = None
        self._receiver_thread = None

        self._logger.notice("finish succeeded")
        self._logger.debug("Speaker.finish LEAVE")

        return True

    def _play(self, audio_out, stream, stop):
        """
        _play - plays audio data from the Speaker queue callback for portaudio
        """
        while not stop.is_set():
            try:
                if self._microphone is not None and self._microphone.is_muted():
                    with self._lock_wait:
                        delta = datetime.now() - self._last_datagram
                        diff_in_ms = delta.total_seconds() * 1000
                        if diff_in_ms > float(self._last_play_delta_in_ms):
                            self._logger.debug(
                                "LastPlay delta is greater than threshold. Unmute!"
                            )
                            self._microphone.unmute()

                data = audio_out.get(True, TIMEOUT)
                with self._lock_wait:
                    self._last_datagram = datetime.now()
                    if self._microphone is not None and not self._microphone.is_muted():
                        self._logger.debug("New speaker sound detected. Mute!")
                        self._microphone.mute()
                stream.write(data)
            except queue.Empty:
                pass
            except Exception as e:  # pylint: disable=broad-except
                self._logger.error("_play exception: %s", str(e))


================================================
File: deepgram/clients/__init__.py
================================================
# Copyright 2023-2024 Deepgram SDK contributors. All Rights Reserved.
# Use of this source code is governed by a MIT license that can be found in the LICENSE file.
# SPDX-License-Identifier: MIT

# common
from .common import (
    TextSource,
    BufferSource,
    StreamSource,
    FileSource,
    UrlSource,
)
from .common import BaseResponse

# common (shared between analze and prerecorded)
from .common import (
    Average,
    Intent,
    Intents,
    IntentsInfo,
    Segment,
    SentimentInfo,
    Sentiment,
    Sentiments,
    SummaryInfo,
    Topic,
    Topics,
    TopicsInfo,
)

# common (shared between listen rest and websocket)
from .common import (
    ModelInfo,
    Hit,
    Search,
)
from .common import (
    OpenResponse,
    CloseResponse,
    UnhandledResponse,
    ErrorResponse,
)
from .common import (
    DeepgramError,
    DeepgramTypeError,
    DeepgramApiError,
    DeepgramUnknownApiError,
)
from .errors import DeepgramModuleError

from .listen_router import ListenRouter
from .read_router import ReadRouter
from .speak_router import SpeakRouter
from .agent_router import AgentRouter

# listen
from .listen import LiveTranscriptionEvents

## backward compat
from .prerecorded import (
    PreRecordedClient,
    AsyncPreRecordedClient,
)
from .live import (
    LiveClient,
    AsyncLiveClient,
)

# speech-to-text rest
from .listen import ListenRESTClient, AsyncListenRESTClient

## input
from .listen import (
    # common
    # UrlSource,
    # BufferSource,
    # StreamSource,
    # TextSource,
    # FileSource,
    # unique
    PreRecordedStreamSource,
    PrerecordedSource,
    ListenRestSource,
)

from .listen import (
    ListenRESTOptions,
    PrerecordedOptions,
)

## output
from .listen import (
    #### top level
    AsyncPrerecordedResponse,
    PrerecordedResponse,
    SyncPrerecordedResponse,
    #### shared
    # Average,
    # Intent,
    # Intents,
    # IntentsInfo,
    # Segment,
    # SentimentInfo,
    # Sentiment,
    # Sentiments,
    # SummaryInfo,
    # Topic,
    # Topics,
    # TopicsInfo,
    #### between rest and websocket
    # ModelInfo,
    # Alternative,
    # Hit,
    # Search,
    # Channel,
    # Word,
    # unique
    Entity,
    ListenRESTMetadata,
    Paragraph,
    Paragraphs,
    ListenRESTResults,
    Sentence,
    Summaries,
    SummaryV1,
    SummaryV2,
    Translation,
    Utterance,
    Warning,
    ListenRESTAlternative,
    ListenRESTChannel,
    ListenRESTWord,
)


# speech-to-text websocket
from .listen import ListenWebSocketClient, AsyncListenWebSocketClient

## input
from .listen import (
    ListenWebSocketOptions,
    LiveOptions,
)

## output
from .listen import (
    #### top level
    LiveResultResponse,
    ListenWSMetadataResponse,
    SpeechStartedResponse,
    UtteranceEndResponse,
    #### common websocket response
    # OpenResponse,
    # CloseResponse,
    # ErrorResponse,
    # UnhandledResponse,
    #### uniqye
    ListenWSMetadata,
    ListenWSWord,
    ListenWSAlternative,
    ListenWSChannel,
)

## clients
from .listen import (
    ListenWebSocketClient,
    AsyncListenWebSocketClient,
)


# read/analyze
from .analyze import ReadClient, AsyncReadClient
from .analyze import AnalyzeClient, AsyncAnalyzeClient
from .analyze import AnalyzeOptions
from .analyze import (
    # common
    # UrlSource,
    # TextSource,
    # BufferSource,
    # StreamSource,
    # FileSource
    # unique
    AnalyzeStreamSource,
    AnalyzeSource,
)
from .analyze import (
    #### top level
    AsyncAnalyzeResponse,
    SyncAnalyzeResponse,
    AnalyzeResponse,
    #### shared between analyze and pre-recorded
    # Average,
    # Intent,
    # Intents,
    # IntentsInfo,
    # Segment,
    # SentimentInfo,
    # Sentiment,
    # Sentiments,
    # SummaryInfo,
    # Topic,
    # Topics,
    # TopicsInfo,
    #### unique
    AnalyzeMetadata,
    AnalyzeResults,
    AnalyzeSummary,
)

# text-to-speech
## text-to-speech REST
from .speak import (
    #### top level
    SpeakRESTOptions,
    SpeakOptions,
    # common
    # TextSource,
    # BufferSource,
    # StreamSource,
    # FileSource,
    # unique
    SpeakSource,
    SpeakRestSource,
    SpeakRESTSource,
)

from .speak import (
    SpeakClient,  # backward compat
    SpeakRESTClient,
    AsyncSpeakRESTClient,
)

from .speak import (
    SpeakResponse,  # backward compat
    SpeakRESTResponse,
)

## text-to-speech WebSocket
from .speak import SpeakWebSocketEvents, SpeakWebSocketMessage

from .speak import (
    SpeakWSOptions,
)

from .speak import (
    SpeakWebSocketClient,
    AsyncSpeakWebSocketClient,
    SpeakWSClient,
    AsyncSpeakWSClient,
)

from .speak import (
    #### top level
    SpeakWSMetadataResponse,
    FlushedResponse,
    ClearedResponse,
    WarningResponse,
    #### common websocket response
    # OpenResponse,
    # CloseResponse,
    # UnhandledResponse,
    # ErrorResponse,
)

# manage
from .manage import ManageClient, AsyncManageClient
from .manage import (
    ProjectOptions,
    KeyOptions,
    ScopeOptions,
    InviteOptions,
    UsageRequestOptions,
    UsageSummaryOptions,
    UsageFieldsOptions,
)
from .manage import (
    #### top level
    Message,
    ProjectsResponse,
    ModelResponse,
    ModelsResponse,
    MembersResponse,
    KeyResponse,
    KeysResponse,
    ScopesResponse,
    InvitesResponse,
    UsageRequest,
    UsageResponse,
    UsageRequestsResponse,
    UsageSummaryResponse,
    UsageFieldsResponse,
    BalancesResponse,
    #### shared
    Project,
    STTDetails,
    TTSMetadata,
    TTSDetails,
    Member,
    Key,
    Invite,
    Config,
    STTUsageDetails,
    Callback,
    TokenDetail,
    SpeechSegment,
    TTSUsageDetails,
    STTTokens,
    TTSTokens,
    UsageSummaryResults,
    Resolution,
    UsageModel,
    Balance,
)

# selfhosted
from .selfhosted import (
    OnPremClient,
    AsyncOnPremClient,
    SelfHostedClient,
    AsyncSelfHostedClient,
)

# agent
from .agent import AgentWebSocketEvents

# websocket
from .agent import (
    AgentWebSocketClient,
    AsyncAgentWebSocketClient,
)

from .agent import (
    #### common websocket response
    # OpenResponse,
    # CloseResponse,
    # ErrorResponse,
    # UnhandledResponse,
    #### unique
    WelcomeResponse,
    SettingsAppliedResponse,
    ConversationTextResponse,
    UserStartedSpeakingResponse,
    AgentThinkingResponse,
    FunctionCalling,
    FunctionCallRequest,
    AgentStartedSpeakingResponse,
    AgentAudioDoneResponse,
    InjectionRefusedResponse,
)

from .agent import (
    # top level
    SettingsConfigurationOptions,
    UpdateInstructionsOptions,
    UpdateSpeakOptions,
    InjectAgentMessageOptions,
    FunctionCallResponse,
    AgentKeepAlive,
    # sub level
    Listen,
    Speak,
    Header,
    Item,
    Properties,
    Parameters,
    Function,
    Provider,
    Think,
    Agent,
    Input,
    Output,
    Audio,
    Context,
)


================================================
File: deepgram/clients/agent_router.py
================================================
# Copyright 2024 Deepgram SDK contributors. All Rights Reserved.
# Use of this source code is governed by a MIT license that can be found in the LICENSE file.
# SPDX-License-Identifier: MIT

from importlib import import_module
import logging

from ..utils import verboselogs
from ..options import DeepgramClientOptions
from .errors import DeepgramModuleError


class AgentRouter:
    """
    Represents a client for interacting with the Deepgram API.

    This class provides a client for making requests to the Deepgram API with various configuration options.

    Attributes:
        config_options (DeepgramClientOptions): An optional configuration object specifying client options.

    Raises:
        DeepgramApiKeyError: If the API key is missing or invalid.

    Methods:
        read: (Preferred) Returns an Threaded AnalyzeClient instance for interacting with Deepgram's read transcription services.
        asyncread: Returns an (Async) AnalyzeClient instance for interacting with Deepgram's read transcription services.
    """

    _logger: verboselogs.VerboseLogger
    _config: DeepgramClientOptions

    def __init__(self, config: DeepgramClientOptions):
        self._logger = verboselogs.VerboseLogger(__name__)
        self._logger.addHandler(logging.StreamHandler())
        self._logger.setLevel(config.verbose)
        self._config = config

    @property
    def websocket(self):
        """
        Returns an AgentWebSocketClient instance for interacting with Deepgram's Agent API.
        """
        return self.Version(self._config, "websocket")

    @property
    def asyncwebsocket(self):
        """
        Returns an AsyncAgentWebSocketClient instance for interacting with Deepgram's Agent API.
        """
        return self.Version(self._config, "asyncwebsocket")

    # INTERNAL CLASSES
    class Version:
        """
        Represents a version of the Deepgram API.
        """

        _logger: verboselogs.VerboseLogger
        _config: DeepgramClientOptions
        _parent: str

        def __init__(self, config, parent: str):
            self._logger = verboselogs.VerboseLogger(__name__)
            self._logger.addHandler(logging.StreamHandler())
            self._logger.setLevel(config.verbose)
            self._config = config
            self._parent = parent

        # FUTURE VERSIONING:
        # When v2 or v1.1beta1 or etc. This allows easy access to the latest version of the API.
        # @property
        # def latest(self):
        #     match self._parent:
        #         case "analyze":
        #             return AnalyzeClient(self._config)
        #         case _:
        #             raise DeepgramModuleError("Invalid parent")

        def v(self, version: str = ""):
            """
            Returns a specific version of the Deepgram API.
            """
            self._logger.debug("Version.v ENTER")
            self._logger.info("version: %s", version)
            if len(version) == 0:
                self._logger.error("version is empty")
                self._logger.debug("Version.v LEAVE")
                raise DeepgramModuleError("Invalid module version")

            parent = ""
            file_name = ""
            class_name = ""
            match self._parent:
                case "websocket":
                    parent = "websocket"
                    file_name = "client"
                    class_name = "AgentWebSocketClient"
                case "asyncwebsocket":
                    parent = "websocket"
                    file_name = "async_client"
                    class_name = "AsyncAgentWebSocketClient"
                case _:
                    self._logger.error("parent unknown: %s", self._parent)
                    self._logger.debug("Version.v LEAVE")
                    raise DeepgramModuleError("Invalid parent type")

            # create class path
            path = f"deepgram.clients.agent.v{version}.{parent}.{file_name}"
            self._logger.info("path: %s", path)
            self._logger.info("class_name: %s", class_name)

            # import class
            mod = import_module(path)
            if mod is None:
                self._logger.error("module path is None")
                self._logger.debug("Version.v LEAVE")
                raise DeepgramModuleError("Unable to find package")

            my_class = getattr(mod, class_name)
            if my_class is None:
                self._logger.error("my_class is None")
                self._logger.debug("Version.v LEAVE")
                raise DeepgramModuleError("Unable to find class")

            # instantiate class
            my_class = my_class(self._config)
            self._logger.notice("Version.v succeeded")
            self._logger.debug("Version.v LEAVE")
            return my_class


================================================
File: deepgram/clients/errors.py
================================================
# Copyright 2023-2024 Deepgram SDK contributors. All Rights Reserved.
# Use of this source code is governed by a MIT license that can be found in the LICENSE file.
# SPDX-License-Identifier: MIT


class DeepgramModuleError(Exception):
    """
    Base class for exceptions raised for a missing Deepgram module.

    Attributes:
        message (str): The error message describing the exception.
    """

    def __init__(self, message: str):
        super().__init__(message)
        self.name = "DeepgramModuleError"


================================================
File: deepgram/clients/listen_router.py
================================================
# Copyright 2023-2024 Deepgram SDK contributors. All Rights Reserved.
# Use of this source code is governed by a MIT license that can be found in the LICENSE file.
# SPDX-License-Identifier: MIT

from importlib import import_module
import logging
import deprecation  # type: ignore

from .. import __version__
from .listen.v1 import (
    PreRecordedClient,
    AsyncPreRecordedClient,
    LiveClient,
    AsyncLiveClient,
)
from ..utils import verboselogs
from ..options import DeepgramClientOptions
from .errors import DeepgramModuleError


class ListenRouter:
    """
    Represents a client for interacting with the Deepgram API.

    This class provides a client for making requests to the Deepgram API with various configuration options.

    Attributes:
        config_options (DeepgramClientOptions): An optional configuration object specifying client options.

    Raises:
        DeepgramApiKeyError: If the API key is missing or invalid.

    Methods:
        live: (Preferred) Returns a Threaded LiveClient instance for interacting with Deepgram's transcription services.
        prerecorded: (Preferred) Returns an Threaded PreRecordedClient instance for interacting with Deepgram's prerecorded transcription services.

        asynclive: Returns an (Async) LiveClient instance for interacting with Deepgram's transcription services.
        asyncprerecorded: Returns an (Async) PreRecordedClient instance for interacting with Deepgram's prerecorded transcription services.
    """

    _logger: verboselogs.VerboseLogger
    _config: DeepgramClientOptions

    def __init__(self, config: DeepgramClientOptions):
        self._logger = verboselogs.VerboseLogger(__name__)
        self._logger.addHandler(logging.StreamHandler())
        self._logger.setLevel(config.verbose)
        self._config = config

    @property
    @deprecation.deprecated(
        deprecated_in="3.4.0",
        removed_in="4.0.0",
        current_version=__version__,
        details="deepgram.listen.prerecorded is deprecated. Use deepgram.listen.rest instead.",
    )
    def prerecorded(self):
        """
        DEPRECATED: deepgram.listen.prerecorded is deprecated. Use deepgram.listen.rest instead.
        """
        return self.Version(self._config, "prerecorded")

    @property
    @deprecation.deprecated(
        deprecated_in="3.4.0",
        removed_in="4.0.0",
        current_version=__version__,
        details="deepgram.listen.asyncprerecorded is deprecated. Use deepgram.listen.asyncrest instead.",
    )
    def asyncprerecorded(self):
        """
        DEPRECATED: deepgram.listen.asyncprerecorded is deprecated. Use deepgram.listen.asyncrest instead.
        """
        return self.Version(self._config, "asyncprerecorded")

    @property
    @deprecation.deprecated(
        deprecated_in="3.4.0",
        removed_in="4.0.0",
        current_version=__version__,
        details="deepgram.listen.live is deprecated. Use deepgram.listen.websocket instead.",
    )
    def live(self):
        """
        DEPRECATED: deepgram.listen.live is deprecated. Use deepgram.listen.websocket instead.
        """
        return self.Version(self._config, "live")

    @property
    @deprecation.deprecated(
        deprecated_in="3.4.0",
        removed_in="4.0.0",
        current_version=__version__,
        details="deepgram.listen.asynclive is deprecated. Use deepgram.listen.asyncwebsocket instead.",
    )
    def asynclive(self):
        """
        DEPRECATED: deepgram.listen.asynclive is deprecated. Use deepgram.listen.asyncwebsocket instead.
        """
        return self.Version(self._config, "asynclive")

    @property
    def rest(self):
        """
        Returns a ListenRESTClient instance for interacting with Deepgram's prerecorded transcription services.
        """
        return self.Version(self._config, "rest")

    @property
    def asyncrest(self):
        """
        Returns an AsyncListenRESTClient instance for interacting with Deepgram's prerecorded transcription services.
        """
        return self.Version(self._config, "asyncrest")

    @property
    def websocket(self):
        """
        Returns a ListenWebSocketClient instance for interacting with Deepgram's transcription services.
        """
        return self.Version(self._config, "websocket")

    @property
    def asyncwebsocket(self):
        """
        Returns an AsyncListenWebSocketClient instance for interacting with Deepgram's transcription services.
        """
        return self.Version(self._config, "asyncwebsocket")

    # INTERNAL CLASSES
    class Version:
        """
        Represents a version of the Deepgram API.
        """

        _logger: verboselogs.VerboseLogger
        _config: DeepgramClientOptions
        _parent: str

        def __init__(self, config, parent: str):
            self._logger = verboselogs.VerboseLogger(__name__)
            self._logger.addHandler(logging.StreamHandler())
            self._logger.setLevel(config.verbose)
            self._config = config
            self._parent = parent

        # FUTURE VERSIONING:
        # When v2 or v1.1beta1 or etc. This allows easy access to the latest version of the API.
        # @property
        # def latest(self):
        #     match self._parent:
        #         case "live":
        #             return LiveClient(self._config)
        #         case "prerecorded":
        #             return PreRecordedClient(self._config)
        #         case _:
        #             raise DeepgramModuleError("Invalid parent")

        def v(self, version: str = ""):
            """
            Returns a specific version of the Deepgram API.
            """
            self._logger.debug("Version.v ENTER")
            self._logger.info("version: %s", version)
            if len(version) == 0:
                self._logger.error("version is empty")
                self._logger.debug("Version.v LEAVE")
                raise DeepgramModuleError("Invalid module version")

            protocol = ""
            file_name = ""
            class_name = ""
            match self._parent:
                case "live":
                    return LiveClient(self._config)
                case "asynclive":
                    return AsyncLiveClient(self._config)
                case "prerecorded":
                    return PreRecordedClient(self._config)
                case "asyncprerecorded":
                    return AsyncPreRecordedClient(self._config)
                case "websocket":
                    protocol = "websocket"
                    file_name = "client"
                    class_name = "ListenWebSocketClient"
                case "asyncwebsocket":
                    protocol = "websocket"
                    file_name = "async_client"
                    class_name = "AsyncListenWebSocketClient"
                case "rest":
                    protocol = "rest"
                    file_name = "client"
                    class_name = "ListenRESTClient"
                case "asyncrest":
                    protocol = "rest"
                    file_name = "async_client"
                    class_name = "AsyncListenRESTClient"
                case _:
                    self._logger.error("parent unknown: %s", self._parent)
                    self._logger.debug("Version.v LEAVE")
                    raise DeepgramModuleError("Invalid parent type")

            # create class path
            path = f"deepgram.clients.listen.v{version}.{protocol}.{file_name}"
            self._logger.info("path: %s", path)
            self._logger.info("class_name: %s", class_name)

            # import class
            mod = import_module(path)
            if mod is None:
                self._logger.error("module path is None")
                self._logger.debug("Version.v LEAVE")
                raise DeepgramModuleError("Unable to find package")

            my_class = getattr(mod, class_name)
            if my_class is None:
                self._logger.error("my_class is None")
                self._logger.debug("Version.v LEAVE")
                raise DeepgramModuleError("Unable to find class")

            # instantiate class
            my_class = my_class(self._config)
            self._logger.notice("Version.v succeeded")
            self._logger.debug("Version.v LEAVE")
            return my_class


================================================
File: deepgram/clients/read_router.py
================================================
# Copyright 2024 Deepgram SDK contributors. All Rights Reserved.
# Use of this source code is governed by a MIT license that can be found in the LICENSE file.
# SPDX-License-Identifier: MIT

from importlib import import_module
import logging

from ..utils import verboselogs
from ..options import DeepgramClientOptions
from .errors import DeepgramModuleError


class ReadRouter:
    """
    Represents a client for interacting with the Deepgram API.

    This class provides a client for making requests to the Deepgram API with various configuration options.

    Attributes:
        config_options (DeepgramClientOptions): An optional configuration object specifying client options.

    Raises:
        DeepgramApiKeyError: If the API key is missing or invalid.

    Methods:
        read: (Preferred) Returns an Threaded AnalyzeClient instance for interacting with Deepgram's read transcription services.
        asyncread: Returns an (Async) AnalyzeClient instance for interacting with Deepgram's read transcription services.
    """

    _logger: verboselogs.VerboseLogger
    _config: DeepgramClientOptions

    def __init__(self, config: DeepgramClientOptions):
        self._logger = verboselogs.VerboseLogger(__name__)
        self._logger.addHandler(logging.StreamHandler())
        self._logger.setLevel(config.verbose)
        self._config = config

    @property
    def analyze(self):
        """
        Returns an AnalyzeClient instance for interacting with Deepgram's read services.
        """
        return self.Version(self._config, "analyze")

    @property
    def asyncanalyze(self):
        """
        Returns an AsyncAnalyzeClient instance for interacting with Deepgram's read services.
        """
        return self.Version(self._config, "asyncanalyze")

    # INTERNAL CLASSES
    class Version:
        """
        Represents a version of the Deepgram API.
        """

        _logger: verboselogs.VerboseLogger
        _config: DeepgramClientOptions
        _parent: str

        def __init__(self, config, parent: str):
            self._logger = verboselogs.VerboseLogger(__name__)
            self._logger.addHandler(logging.StreamHandler())
            self._logger.setLevel(config.verbose)
            self._config = config
            self._parent = parent

        # FUTURE VERSIONING:
        # When v2 or v1.1beta1 or etc. This allows easy access to the latest version of the API.
        # @property
        # def latest(self):
        #     match self._parent:
        #         case "analyze":
        #             return AnalyzeClient(self._config)
        #         case _:
        #             raise DeepgramModuleError("Invalid parent")

        def v(self, version: str = ""):
            """
            Returns a specific version of the Deepgram API.
            """
            self._logger.debug("Version.v ENTER")
            self._logger.info("version: %s", version)
            if len(version) == 0:
                self._logger.error("version is empty")
                self._logger.debug("Version.v LEAVE")
                raise DeepgramModuleError("Invalid module version")

            parent = ""
            file_name = ""
            class_name = ""
            match self._parent:
                case "analyze":
                    parent = "analyze"
                    file_name = "client"
                    class_name = "AnalyzeClient"
                case "asyncanalyze":
                    parent = "analyze"
                    file_name = "async_client"
                    class_name = "AsyncAnalyzeClient"
                case _:
                    self._logger.error("parent unknown: %s", self._parent)
                    self._logger.debug("Version.v LEAVE")
                    raise DeepgramModuleError("Invalid parent type")

            # create class path
            path = f"deepgram.clients.{parent}.v{version}.{file_name}"
            self._logger.info("path: %s", path)
            self._logger.info("class_name: %s", class_name)

            # import class
            mod = import_module(path)
            if mod is None:
                self._logger.error("module path is None")
                self._logger.debug("Version.v LEAVE")
                raise DeepgramModuleError("Unable to find package")

            my_class = getattr(mod, class_name)
            if my_class is None:
                self._logger.error("my_class is None")
                self._logger.debug("Version.v LEAVE")
                raise DeepgramModuleError("Unable to find class")

            # instantiate class
            my_class = my_class(self._config)
            self._logger.notice("Version.v succeeded")
            self._logger.debug("Version.v LEAVE")
            return my_class


================================================
File: deepgram/clients/speak_router.py
================================================
# Copyright 2023-2024 Deepgram SDK contributors. All Rights Reserved.
# Use of this source code is governed by a MIT license that can be found in the LICENSE file.
# SPDX-License-Identifier: MIT

from importlib import import_module
import logging
import deprecation  # type: ignore

from .. import __version__
from .speak.v1.rest.client import SpeakRESTClient
from ..utils import verboselogs
from ..options import DeepgramClientOptions
from .errors import DeepgramModuleError


class SpeakRouter:
    """
    This class provides a Speak Clients for making requests to the Deepgram API with various configuration options.

    Attributes:
        config_options (DeepgramClientOptions): An optional configuration object specifying client options.

    Methods:
        rest: (Preferred) Returns a Threaded REST Client instance for interacting with Deepgram's transcription services.
        websocket: (Preferred) Returns an Threaded WebSocket Client instance for interacting with Deepgram's prerecorded transcription services.

        asyncrest: Returns an Async REST Client instance for interacting with Deepgram's transcription services.
        asyncwebsocket: Returns an Async WebSocket Client instance for interacting with Deepgram's prerecorded transcription services.
    """

    _logger: verboselogs.VerboseLogger
    _config: DeepgramClientOptions

    def __init__(self, config: DeepgramClientOptions):
        self._logger = verboselogs.VerboseLogger(__name__)
        self._logger.addHandler(logging.StreamHandler())
        self._logger.setLevel(config.verbose)
        self._config = config

    # when this is removed, remove --disable=W0622 from Makefile
    # pylint: disable=unused-argument
    @deprecation.deprecated(
        deprecated_in="3.4.0",
        removed_in="4.0.0",
        current_version=__version__,
        details="deepgram.speak.v1 is deprecated. Use deepgram.speak.rest or deepgram.speak.websocket instead.",
    )
    def v(self, version: str = ""):
        """
        DEPRECATED: deepgram.speak.v1 is deprecated. Use deepgram.speak.rest or deepgram.speak.websocket instead.
        """
        return SpeakRESTClient(self._config)

    # pylint: enable=unused-argument

    @property
    def rest(self):
        """
        Returns a Threaded REST Client instance for interacting with Deepgram's prerecorded Text-to-Speech services.
        """
        return self.Version(self._config, "rest")

    @property
    def asyncrest(self):
        """
        Returns an Async REST Client instance for interacting with Deepgram's prerecorded Text-to-Speech services.
        """
        return self.Version(self._config, "asyncrest")

    @property
    def websocket(self):
        """
        Returns a Threaded WebSocket Client instance for interacting with Deepgram's Text-to-Speech services.
        """
        return self.Version(self._config, "websocket")

    @property
    def asyncwebsocket(self):
        """
        Returns an Async WebSocket Client instance for interacting with Deepgram's Text-to-Speech services.
        """
        return self.Version(self._config, "asyncwebsocket")

    # INTERNAL CLASSES
    class Version:
        """
        Represents a version of the Deepgram API.
        """

        _logger: verboselogs.VerboseLogger
        _config: DeepgramClientOptions
        _parent: str

        def __init__(self, config, parent: str):
            self._logger = verboselogs.VerboseLogger(__name__)
            self._logger.addHandler(logging.StreamHandler())
            self._logger.setLevel(config.verbose)
            self._config = config
            self._parent = parent

        # FUTURE VERSIONING:
        # When v2 or v1.1beta1 or etc. This allows easy access to the latest version of the API.
        # @property
        # def latest(self):
        #     match self._parent:
        #         case "live":
        #             return LiveClient(self._config)
        #         case "prerecorded":
        #             return PreRecordedClient(self._config)
        #         case _:
        #             raise DeepgramModuleError("Invalid parent")

        def v(self, version: str = ""):
            """
            Returns a specific version of the Deepgram API.
            """
            self._logger.debug("Version.v ENTER")
            self._logger.info("version: %s", version)
            if len(version) == 0:
                self._logger.error("version is empty")
                self._logger.debug("Version.v LEAVE")
                raise DeepgramModuleError("Invalid module version")

            type = ""
            file_name = ""
            class_name = ""
            match self._parent:
                case "websocket":
                    type = "websocket"
                    file_name = "client"
                    class_name = "SpeakWebSocketClient"
                case "asyncwebsocket":
                    type = "websocket"
                    file_name = "async_client"
                    class_name = "AsyncSpeakWebSocketClient"
                case "rest":
                    type = "rest"
                    file_name = "client"
                    class_name = "SpeakRESTClient"
                case "asyncrest":
                    type = "rest"
                    file_name = "async_client"
                    class_name = "AsyncSpeakRESTClient"
                case _:
                    self._logger.error("parent unknown: %s", self._parent)
                    self._logger.debug("Version.v LEAVE")
                    raise DeepgramModuleError("Invalid parent type")

            # create class path
            path = f"deepgram.clients.speak.v{version}.{type}.{file_name}"
            self._logger.info("path: %s", path)
            self._logger.info("class_name: %s", class_name)

            # import class
            mod = import_module(path)
            if mod is None:
                self._logger.error("module path is None")
                self._logger.debug("Version.v LEAVE")
                raise DeepgramModuleError("Unable to find package")

            my_class = getattr(mod, class_name)
            if my_class is None:
                self._logger.error("my_class is None")
                self._logger.debug("Version.v LEAVE")
                raise DeepgramModuleError("Unable to find class")

            # instantiate class
            my_class = my_class(self._config)
            self._logger.notice("Version.v succeeded")
            self._logger.debug("Version.v LEAVE")
            return my_class


================================================
File: deepgram/clients/agent/__init__.py
================================================
# Copyright 2023-2024 Deepgram SDK contributors. All Rights Reserved.
# Use of this source code is governed by a MIT license that can be found in the LICENSE file.
# SPDX-License-Identifier: MIT

from .enums import AgentWebSocketEvents

# websocket
from .client import (
    AgentWebSocketClient,
    AsyncAgentWebSocketClient,
)

from .client import (
    #### common websocket response
    OpenResponse,
    CloseResponse,
    ErrorResponse,
    UnhandledResponse,
    #### unique
    WelcomeResponse,
    SettingsAppliedResponse,
    ConversationTextResponse,
    UserStartedSpeakingResponse,
    AgentThinkingResponse,
    FunctionCalling,
    FunctionCallRequest,
    AgentStartedSpeakingResponse,
    AgentAudioDoneResponse,
    InjectionRefusedResponse,
)

from .client import (
    # top level
    SettingsConfigurationOptions,
    UpdateInstructionsOptions,
    UpdateSpeakOptions,
    InjectAgentMessageOptions,
    FunctionCallResponse,
    AgentKeepAlive,
    # sub level
    Listen,
    Speak,
    Header,
    Item,
    Properties,
    Parameters,
    Function,
    Provider,
    Think,
    Agent,
    Input,
    Output,
    Audio,
    Context,
)


================================================
File: deepgram/clients/agent/client.py
================================================
# Copyright 2024 Deepgram SDK contributors. All Rights Reserved.
# Use of this source code is governed by a MIT license that can be found in the LICENSE file.
# SPDX-License-Identifier: MIT

# websocket
from .v1 import (
    AgentWebSocketClient as LatestAgentWebSocketClient,
    AsyncAgentWebSocketClient as LatestAsyncAgentWebSocketClient,
)

from .v1 import (
    #### common websocket response
    BaseResponse as LatestBaseResponse,
    OpenResponse as LatestOpenResponse,
    CloseResponse as LatestCloseResponse,
    ErrorResponse as LatestErrorResponse,
    UnhandledResponse as LatestUnhandledResponse,
    #### unique
    WelcomeResponse as LatestWelcomeResponse,
    SettingsAppliedResponse as LatestSettingsAppliedResponse,
    ConversationTextResponse as LatestConversationTextResponse,
    UserStartedSpeakingResponse as LatestUserStartedSpeakingResponse,
    AgentThinkingResponse as LatestAgentThinkingResponse,
    FunctionCalling as LatestFunctionCalling,
    FunctionCallRequest as LatestFunctionCallRequest,
    AgentStartedSpeakingResponse as LatestAgentStartedSpeakingResponse,
    AgentAudioDoneResponse as LatestAgentAudioDoneResponse,
    InjectionRefusedResponse as LatestInjectionRefusedResponse,
)

from .v1 import (
    # top level
    SettingsConfigurationOptions as LatestSettingsConfigurationOptions,
    UpdateInstructionsOptions as LatestUpdateInstructionsOptions,
    UpdateSpeakOptions as LatestUpdateSpeakOptions,
    InjectAgentMessageOptions as LatestInjectAgentMessageOptions,
    FunctionCallResponse as LatestFunctionCallResponse,
    AgentKeepAlive as LatestAgentKeepAlive,
    # sub level
    Listen as LatestListen,
    Speak as LatestSpeak,
    Header as LatestHeader,
    Item as LatestItem,
    Properties as LatestProperties,
    Parameters as LatestParameters,
    Function as LatestFunction,
    Provider as LatestProvider,
    Think as LatestThink,
    Agent as LatestAgent,
    Input as LatestInput,
    Output as LatestOutput,
    Audio as LatestAudio,
    Context as LatestContext,
)


# The vX/client.py points to the current supported version in the SDK.
# Older versions are supported in the SDK for backwards compatibility.

AgentWebSocketClient = LatestAgentWebSocketClient
AsyncAgentWebSocketClient = LatestAsyncAgentWebSocketClient

OpenResponse = LatestOpenResponse
CloseResponse = LatestCloseResponse
ErrorResponse = LatestErrorResponse
UnhandledResponse = LatestUnhandledResponse

WelcomeResponse = LatestWelcomeResponse
SettingsAppliedResponse = LatestSettingsAppliedResponse
ConversationTextResponse = LatestConversationTextResponse
UserStartedSpeakingResponse = LatestUserStartedSpeakingResponse
AgentThinkingResponse = LatestAgentThinkingResponse
FunctionCalling = LatestFunctionCalling
FunctionCallRequest = LatestFunctionCallRequest
AgentStartedSpeakingResponse = LatestAgentStartedSpeakingResponse
AgentAudioDoneResponse = LatestAgentAudioDoneResponse
InjectionRefusedResponse = LatestInjectionRefusedResponse


SettingsConfigurationOptions = LatestSettingsConfigurationOptions
UpdateInstructionsOptions = LatestUpdateInstructionsOptions
UpdateSpeakOptions = LatestUpdateSpeakOptions
InjectAgentMessageOptions = LatestInjectAgentMessageOptions
FunctionCallResponse = LatestFunctionCallResponse
AgentKeepAlive = LatestAgentKeepAlive

Listen = LatestListen
Speak = LatestSpeak
Header = LatestHeader
Item = LatestItem
Properties = LatestProperties
Parameters = LatestParameters
Function = LatestFunction
Provider = LatestProvider
Think = LatestThink
Agent = LatestAgent
Input = LatestInput
Output = LatestOutput
Audio = LatestAudio
Context = LatestContext


================================================
File: deepgram/clients/agent/enums.py
================================================
# Copyright 2023-2024 Deepgram SDK contributors. All Rights Reserved.
# Use of this source code is governed by a MIT license that can be found in the LICENSE file.
# SPDX-License-Identifier: MIT

from aenum import StrEnum

# Constants mapping to events from the Deepgram API


class AgentWebSocketEvents(StrEnum):
    """
    Enumerates the possible Agent API events that can be received from the Deepgram API
    """

    # server
    Open: str = "Open"
    Close: str = "Close"
    AudioData: str = "AudioData"
    Welcome: str = "Welcome"
    SettingsApplied: str = "SettingsApplied"
    ConversationText: str = "ConversationText"
    UserStartedSpeaking: str = "UserStartedSpeaking"
    AgentThinking: str = "AgentThinking"
    FunctionCalling: str = "FunctionCalling"
    FunctionCallRequest: str = "FunctionCallRequest"
    AgentStartedSpeaking: str = "AgentStartedSpeaking"
    AgentAudioDone: str = "AgentAudioDone"
    Error: str = "Error"
    Unhandled: str = "Unhandled"

    # client
    SettingsConfiguration: str = "SettingsConfiguration"
    UpdateInstructions: str = "UpdateInstructions"
    UpdateSpeak: str = "UpdateSpeak"
    InjectAgentMessage: str = "InjectAgentMessage"
    InjectionRefused: str = "InjectionRefused"
    AgentKeepAlive: str = "AgentKeepAlive"


================================================
File: deepgram/clients/agent/v1/__init__.py
================================================
# Copyright 2024 Deepgram SDK contributors. All Rights Reserved.
# Use of this source code is governed by a MIT license that can be found in the LICENSE file.
# SPDX-License-Identifier: MIT

# common websocket
from ...common import (
    OpenResponse,
    CloseResponse,
    UnhandledResponse,
    ErrorResponse,
)

# websocket
from .websocket import AgentWebSocketClient, AsyncAgentWebSocketClient

from .websocket import (
    #### common websocket response
    BaseResponse,
    OpenResponse,
    CloseResponse,
    ErrorResponse,
    UnhandledResponse,
    #### unique
    WelcomeResponse,
    SettingsAppliedResponse,
    ConversationTextResponse,
    UserStartedSpeakingResponse,
    AgentThinkingResponse,
    FunctionCalling,
    FunctionCallRequest,
    AgentStartedSpeakingResponse,
    AgentAudioDoneResponse,
    InjectionRefusedResponse,
)

from .websocket import (
    # top level
    SettingsConfigurationOptions,
    UpdateInstructionsOptions,
    UpdateSpeakOptions,
    InjectAgentMessageOptions,
    FunctionCallResponse,
    AgentKeepAlive,
    # sub level
    Listen,
    Speak,
    Header,
    Item,
    Properties,
    Parameters,
    Function,
    Provider,
    Think,
    Agent,
    Input,
    Output,
    Audio,
    Context,
)


================================================
File: deepgram/clients/agent/v1/websocket/__init__.py
================================================
# Copyright 2024 Deepgram SDK contributors. All Rights Reserved.
# Use of this source code is governed by a MIT license that can be found in the LICENSE file.
# SPDX-License-Identifier: MIT

from .client import AgentWebSocketClient
from .async_client import AsyncAgentWebSocketClient

from .response import (
    #### common websocket response
    BaseResponse,
    OpenResponse,
    CloseResponse,
    ErrorResponse,
    UnhandledResponse,
    #### unique
    WelcomeResponse,
    SettingsAppliedResponse,
    ConversationTextResponse,
    UserStartedSpeakingResponse,
    AgentThinkingResponse,
    FunctionCalling,
    FunctionCallRequest,
    AgentStartedSpeakingResponse,
    AgentAudioDoneResponse,
    InjectionRefusedResponse,
)
from .options import (
    # top level
    SettingsConfigurationOptions,
    UpdateInstructionsOptions,
    UpdateSpeakOptions,
    InjectAgentMessageOptions,
    FunctionCallResponse,
    AgentKeepAlive,
    # sub level
    Listen,
    Speak,
    Header,
    Item,
    Properties,
    Parameters,
    Function,
    Provider,
    Think,
    Agent,
    Input,
    Output,
    Audio,
    Context,
)


================================================
File: deepgram/clients/agent/v1/websocket/async_client.py
================================================
# Copyright 2024 Deepgram SDK contributors. All Rights Reserved.
# Use of this source code is governed by a MIT license that can be found in the LICENSE file.
# SPDX-License-Identifier: MIT

import asyncio
import json
import logging
from typing import Dict, Union, Optional, cast, Any, Callable
import threading

from .....utils import verboselogs
from .....options import DeepgramClientOptions
from ...enums import AgentWebSocketEvents
from ....common import AbstractAsyncWebSocketClient
from ....common import DeepgramError

from .response import (
    OpenResponse,
    WelcomeResponse,
    SettingsAppliedResponse,
    ConversationTextResponse,
    UserStartedSpeakingResponse,
    AgentThinkingResponse,
    FunctionCalling,
    FunctionCallRequest,
    AgentStartedSpeakingResponse,
    AgentAudioDoneResponse,
    InjectionRefusedResponse,
    CloseResponse,
    ErrorResponse,
    UnhandledResponse,
)
from .options import (
    SettingsConfigurationOptions,
    UpdateInstructionsOptions,
    UpdateSpeakOptions,
    InjectAgentMessageOptions,
    FunctionCallResponse,
    AgentKeepAlive,
)

from .....audio.speaker import (
    Speaker,
    RATE as SPEAKER_RATE,
    CHANNELS as SPEAKER_CHANNELS,
    PLAYBACK_DELTA as SPEAKER_PLAYBACK_DELTA,
)
from .....audio.microphone import (
    Microphone,
    RATE as MICROPHONE_RATE,
    CHANNELS as MICROPHONE_CHANNELS,
)

ONE_SECOND = 1
HALF_SECOND = 0.5
DEEPGRAM_INTERVAL = 5


class AsyncAgentWebSocketClient(
    AbstractAsyncWebSocketClient
):  # pylint: disable=too-many-instance-attributes
    """
    Client for interacting with Deepgram's live transcription services over WebSockets.

     This class provides methods to establish a WebSocket connection for live transcription and handle real-time transcription events.

     Args:
         config (DeepgramClientOptions): all the options for the client.
    """

    _logger: verboselogs.VerboseLogger
    _config: DeepgramClientOptions
    _endpoint: str

    _event_handlers: Dict[AgentWebSocketEvents, list]

    _keep_alive_thread: Union[asyncio.Task, None]

    _kwargs: Optional[Dict] = None
    _addons: Optional[Dict] = None
    # note the distinction here. We can't use _config because it's already used in the parent
    _settings: Optional[SettingsConfigurationOptions] = None
    _headers: Optional[Dict] = None

    _speaker_created: bool = False
    _speaker: Optional[Speaker] = None
    _microphone_created: bool = False
    _microphone: Optional[Microphone] = None

    def __init__(self, config: DeepgramClientOptions):
        if config is None:
            raise DeepgramError("Config is required")

        self._logger = verboselogs.VerboseLogger(__name__)
        self._logger.addHandler(logging.StreamHandler())
        self._logger.setLevel(config.verbose)

        self._config = config

        # needs to be "wss://agent.deepgram.com/agent"
        self._endpoint = "agent"

        # override the endpoint since it needs to be "wss://agent.deepgram.com/agent"
        self._config.url = "agent.deepgram.com"
        self._keep_alive_thread = None

        # init handlers
        self._event_handlers = {
            event: [] for event in AgentWebSocketEvents.__members__.values()
        }

        if self._config.options.get("microphone_record") == "true":
            self._logger.info("microphone_record is enabled")
            rate = self._config.options.get("microphone_record_rate", MICROPHONE_RATE)
            channels = self._config.options.get(
                "microphone_record_channels", MICROPHONE_CHANNELS
            )
            device_index = self._config.options.get("microphone_record_device_index")

            self._logger.debug("rate: %s", rate)
            self._logger.debug("channels: %s", channels)
            if device_index is not None:
                self._logger.debug("device_index: %s", device_index)

            self._microphone_created = True

            if device_index is not None:
                self._microphone = Microphone(
                    rate=rate,
                    channels=channels,
                    verbose=self._config.verbose,
                    input_device_index=device_index,
                )
            else:
                self._microphone = Microphone(
                    rate=rate,
                    channels=channels,
                    verbose=self._config.verbose,
                )

        if self._config.options.get("speaker_playback") == "true":
            self._logger.info("speaker_playback is enabled")
            rate = self._config.options.get("speaker_playback_rate", SPEAKER_RATE)
            channels = self._config.options.get(
                "speaker_playback_channels", SPEAKER_CHANNELS
            )
            playback_delta_in_ms = self._config.options.get(
                "speaker_playback_delta_in_ms", SPEAKER_PLAYBACK_DELTA
            )
            device_index = self._config.options.get("speaker_playback_device_index")

            self._logger.debug("rate: %s", rate)
            self._logger.debug("channels: %s", channels)

            self._speaker_created = True

            if device_index is not None:
                self._logger.debug("device_index: %s", device_index)

                self._speaker = Speaker(
                    rate=rate,
                    channels=channels,
                    last_play_delta_in_ms=playback_delta_in_ms,
                    verbose=self._config.verbose,
                    output_device_index=device_index,
                    microphone=self._microphone,
                )
            else:
                self._speaker = Speaker(
                    rate=rate,
                    channels=channels,
                    last_play_delta_in_ms=playback_delta_in_ms,
                    verbose=self._config.verbose,
                    microphone=self._microphone,
                )
        # call the parent constructor
        super().__init__(self._config, self._endpoint)

    # pylint: disable=too-many-branches,too-many-statements
    async def start(
        self,
        options: Optional[SettingsConfigurationOptions] = None,
        addons: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        members: Optional[Dict] = None,
        **kwargs,
    ) -> bool:
        """
        Starts the WebSocket connection for agent API.
        """
        self._logger.debug("AsyncAgentWebSocketClient.start ENTER")
        self._logger.info("settings: %s", options)
        self._logger.info("addons: %s", addons)
        self._logger.info("headers: %s", headers)
        self._logger.info("members: %s", members)
        self._logger.info("kwargs: %s", kwargs)

        if isinstance(options, SettingsConfigurationOptions) and not options.check():
            self._logger.error("settings.check failed")
            self._logger.debug("AsyncAgentWebSocketClient.start LEAVE")
            raise DeepgramError("Fatal agent settings error")

        self._addons = addons
        self._headers = headers

        # add "members" as members of the class
        if members is not None:
            self.__dict__.update(members)

        # set kwargs as members of the class
        if kwargs is not None:
            self._kwargs = kwargs
        else:
            self._kwargs = {}

        if isinstance(options, SettingsConfigurationOptions):
            self._logger.info("options is class")
            self._settings = options
        elif isinstance(options, dict):
            self._logger.info("options is dict")
            self._settings = SettingsConfigurationOptions.from_dict(options)
        elif isinstance(options, str):
            self._logger.info("options is json")
            self._settings = SettingsConfigurationOptions.from_json(options)
        else:
            raise DeepgramError("Invalid options type")

        try:
            # speaker substitutes the listening thread
            if self._speaker is not None:
                self._logger.notice("passing speaker to delegate_listening")
                super().delegate_listening(self._speaker)

            # call parent start
            if (
                await super().start(
                    {},
                    self._addons,
                    self._headers,
                    **dict(cast(Dict[Any, Any], self._kwargs)),
                )
                is False
            ):
                self._logger.error("AsyncAgentWebSocketClient.start failed")
                self._logger.debug("AsyncAgentWebSocketClient.start LEAVE")
                return False

            if self._speaker is not None:
                self._logger.notice("speaker is delegate_listening. Starting speaker")
                self._speaker.start()

            if self._speaker is not None and self._microphone is not None:
                self._logger.notice(
                    "speaker is delegate_listening. Starting microphone"
                )
                self._microphone.set_callback(self.send)
                self._microphone.start()

            # debug the threads
            for thread in threading.enumerate():
                self._logger.debug("after running thread: %s", thread.name)
            self._logger.debug("number of active threads: %s", threading.active_count())

            # keepalive thread
            if self._config.is_keep_alive_enabled():
                self._logger.notice("keepalive is enabled")
                self._keep_alive_thread = asyncio.create_task(self._keep_alive())
            else:
                self._logger.notice("keepalive is disabled")

            # debug the threads
            for thread in threading.enumerate():
                self._logger.debug("after running thread: %s", thread.name)
            self._logger.debug("number of active threads: %s", threading.active_count())

            # send the configurationsetting message
            self._logger.notice("Sending ConfigurationSettings...")
            ret_send_cs = await self.send(str(self._settings))
            if not ret_send_cs:
                self._logger.error("ConfigurationSettings failed")

                err_error: ErrorResponse = ErrorResponse(
                    "Exception in AsyncAgentWebSocketClient.start",
                    "ConfigurationSettings failed to send",
                    "Exception",
                )
                await self._emit(
                    AgentWebSocketEvents(AgentWebSocketEvents.Error),
                    error=err_error,
                    **dict(cast(Dict[Any, Any], self._kwargs)),
                )

                self._logger.debug("AgentWebSocketClient.start LEAVE")
                return False

            self._logger.notice("start succeeded")
            self._logger.debug("AsyncAgentWebSocketClient.start LEAVE")
            return True

        except Exception as e:  # pylint: disable=broad-except
            self._logger.error(
                "WebSocketException in AsyncAgentWebSocketClient.start: %s", e
            )
            self._logger.debug("AsyncAgentWebSocketClient.start LEAVE")
            if self._config.options.get("termination_exception_connect") is True:
                raise e
            return False

    # pylint: enable=too-many-branches,too-many-statements

    def on(self, event: AgentWebSocketEvents, handler: Callable) -> None:
        """
        Registers event handlers for specific events.
        """
        self._logger.info("event subscribed: %s", event)
        if event in AgentWebSocketEvents.__members__.values() and callable(handler):
            self._event_handlers[event].append(handler)

    async def _emit(self, event: AgentWebSocketEvents, *args, **kwargs) -> None:
        """
        Emits events to the registered event handlers.
        """
        self._logger.debug("AsyncAgentWebSocketClient._emit ENTER")
        self._logger.debug("callback handlers for: %s", event)

        # debug the threads
        for thread in threading.enumerate():
            self._logger.debug("after running thread: %s", thread.name)
        self._logger.debug("number of active threads: %s", threading.active_count())

        self._logger.debug("callback handlers for: %s", event)
        tasks = []
        for handler in self._event_handlers[event]:
            task = asyncio.create_task(handler(self, *args, **kwargs))
            tasks.append(task)

        if tasks:
            self._logger.debug("waiting for tasks to finish...")
            await asyncio.gather(*tasks, return_exceptions=True)
            tasks.clear()

        # debug the threads
        for thread in threading.enumerate():
            self._logger.debug("after running thread: %s", thread.name)
        self._logger.debug("number of active threads: %s", threading.active_count())

        self._logger.debug("AsyncAgentWebSocketClient._emit LEAVE")

    # pylint: disable=too-many-locals,too-many-statements
    async def _process_text(self, message: str) -> None:
        """
        Processes messages received over the WebSocket connection.
        """
        self._logger.debug("AsyncAgentWebSocketClient._process_text ENTER")

        try:
            self._logger.debug("Text data received")
            if len(message) == 0:
                self._logger.debug("message is empty")
                self._logger.debug("AsyncAgentWebSocketClient._process_text LEAVE")
                return

            data = json.loads(message)
            response_type = data.get("type")
            self._logger.debug("response_type: %s, data: %s", response_type, data)

            match response_type:
                case AgentWebSocketEvents.Open:
                    open_result: OpenResponse = OpenResponse.from_json(message)
                    self._logger.verbose("OpenResponse: %s", open_result)
                    await self._emit(
                        AgentWebSocketEvents(AgentWebSocketEvents.Open),
                        open=open_result,
                        **dict(cast(Dict[Any, Any], self._kwargs)),
                    )
                case AgentWebSocketEvents.Welcome:
                    welcome_result: WelcomeResponse = WelcomeResponse.from_json(message)
                    self._logger.verbose("WelcomeResponse: %s", welcome_result)
                    await self._emit(
                        AgentWebSocketEvents(AgentWebSocketEvents.Welcome),
                        welcome=welcome_result,
                        **dict(cast(Dict[Any, Any], self._kwargs)),
                    )
                case AgentWebSocketEvents.SettingsApplied:
                    settings_applied_result: SettingsAppliedResponse = (
                        SettingsAppliedResponse.from_json(message)
                    )
                    self._logger.verbose(
                        "SettingsAppliedResponse: %s", settings_applied_result
                    )
                    await self._emit(
                        AgentWebSocketEvents(AgentWebSocketEvents.SettingsApplied),
                        settings_applied=settings_applied_result,
                        **dict(cast(Dict[Any, Any], self._kwargs)),
                    )
                case AgentWebSocketEvents.ConversationText:
                    conversation_text_result: ConversationTextResponse = (
                        ConversationTextResponse.from_json(message)
                    )
                    self._logger.verbose(
                        "ConversationTextResponse: %s", conversation_text_result
                    )
                    await self._emit(
                        AgentWebSocketEvents(AgentWebSocketEvents.ConversationText),
                        conversation_text=conversation_text_result,
                        **dict(cast(Dict[Any, Any], self._kwargs)),
                    )
                case AgentWebSocketEvents.UserStartedSpeaking:
                    user_started_speaking_result: UserStartedSpeakingResponse = (
                        UserStartedSpeakingResponse.from_json(message)
                    )
                    self._logger.verbose(
                        "UserStartedSpeakingResponse: %s", user_started_speaking_result
                    )
                    await self._emit(
                        AgentWebSocketEvents(AgentWebSocketEvents.UserStartedSpeaking),
                        user_started_speaking=user_started_speaking_result,
                        **dict(cast(Dict[Any, Any], self._kwargs)),
                    )
                case AgentWebSocketEvents.AgentThinking:
                    agent_thinking_result: AgentThinkingResponse = (
                        AgentThinkingResponse.from_json(message)
                    )
                    self._logger.verbose(
                        "AgentThinkingResponse: %s", agent_thinking_result
                    )
                    await self._emit(
                        AgentWebSocketEvents(AgentWebSocketEvents.AgentThinking),
                        agent_thinking=agent_thinking_result,
                        **dict(cast(Dict[Any, Any], self._kwargs)),
                    )
                case AgentWebSocketEvents.FunctionCalling:
                    function_calling_result: FunctionCalling = (
                        FunctionCalling.from_json(message)
                    )
                    self._logger.verbose("FunctionCalling: %s", function_calling_result)
                    await self._emit(
                        AgentWebSocketEvents(AgentWebSocketEvents.FunctionCalling),
                        function_calling=function_calling_result,
                        **dict(cast(Dict[Any, Any], self._kwargs)),
                    )
                case AgentWebSocketEvents.FunctionCallRequest:
                    function_call_request_result: FunctionCallRequest = (
                        FunctionCallRequest.from_json(message)
                    )
                    self._logger.verbose(
                        "FunctionCallRequest: %s", function_call_request_result
                    )
                    await self._emit(
                        AgentWebSocketEvents(AgentWebSocketEvents.FunctionCallRequest),
                        function_call_request=function_call_request_result,
                        **dict(cast(Dict[Any, Any], self._kwargs)),
                    )
                case AgentWebSocketEvents.AgentStartedSpeaking:
                    agent_started_speaking_result: AgentStartedSpeakingResponse = (
                        AgentStartedSpeakingResponse.from_json(message)
                    )
                    self._logger.verbose(
                        "AgentStartedSpeakingResponse: %s",
                        agent_started_speaking_result,
                    )
                    await self._emit(
                        AgentWebSocketEvents(AgentWebSocketEvents.AgentStartedSpeaking),
                        agent_started_speaking=agent_started_speaking_result,
                        **dict(cast(Dict[Any, Any], self._kwargs)),
                    )
                case AgentWebSocketEvents.AgentAudioDone:
                    agent_audio_done_result: AgentAudioDoneResponse = (
                        AgentAudioDoneResponse.from_json(message)
                    )
                    self._logger.verbose(
                        "AgentAudioDoneResponse: %s", agent_audio_done_result
                    )
                    await self._emit(
                        AgentWebSocketEvents(AgentWebSocketEvents.AgentAudioDone),
                        agent_audio_done=agent_audio_done_result,
                        **dict(cast(Dict[Any, Any], self._kwargs)),
                    )
                case AgentWebSocketEvents.InjectionRefused:
                    injection_refused_result: InjectionRefusedResponse = (
                        InjectionRefusedResponse.from_json(message)
                    )
                    self._logger.verbose(
                        "InjectionRefused: %s", injection_refused_result
                    )
                    await self._emit(
                        AgentWebSocketEvents(AgentWebSocketEvents.InjectionRefused),
                        injection_refused=injection_refused_result,
                        **dict(cast(Dict[Any, Any], self._kwargs)),
                    )
                case AgentWebSocketEvents.Close:
                    close_result: CloseResponse = CloseResponse.from_json(message)
                    self._logger.verbose("CloseResponse: %s", close_result)
                    await self._emit(
                        AgentWebSocketEvents(AgentWebSocketEvents.Close),
                        close=close_result,
                        **dict(cast(Dict[Any, Any], self._kwargs)),
                    )
                case AgentWebSocketEvents.Error:
                    err_error: ErrorResponse = ErrorResponse.from_json(message)
                    self._logger.verbose("ErrorResponse: %s", err_error)
                    await self._emit(
                        AgentWebSocketEvents(AgentWebSocketEvents.Error),
                        error=err_error,
                        **dict(cast(Dict[Any, Any], self._kwargs)),
                    )
                case _:
                    self._logger.warning(
                        "Unknown Message: response_type: %s, data: %s",
                        response_type,
                        data,
                    )
                    unhandled_error: UnhandledResponse = UnhandledResponse(
                        type=AgentWebSocketEvents(AgentWebSocketEvents.Unhandled),
                        raw=message,
                    )
                    await self._emit(
                        AgentWebSocketEvents(AgentWebSocketEvents.Unhandled),
                        unhandled=unhandled_error,
                        **dict(cast(Dict[Any, Any], self._kwargs)),
                    )

            self._logger.notice("_process_text Succeeded")
            self._logger.debug("AsyncAgentWebSocketClient._process_text LEAVE")

        except Exception as e:  # pylint: disable=broad-except
            self._logger.error(
                "Exception in AsyncAgentWebSocketClient._process_text: %s", e
            )
            e_error: ErrorResponse = ErrorResponse(
                "Exception in AsyncAgentWebSocketClient._process_text",
                f"{e}",
                "Exception",
            )
            await self._emit(
                AgentWebSocketEvents(AgentWebSocketEvents.Error),
                error=e_error,
                **dict(cast(Dict[Any, Any], self._kwargs)),
            )

            # signal exit and close
            await super()._signal_exit()

            self._logger.debug("AsyncAgentWebSocketClient._process_text LEAVE")

            if self._config.options.get("termination_exception") is True:
                raise
            return

    # pylint: enable=too-many-locals,too-many-statements

    async def _process_binary(self, message: bytes) -> None:
        self._logger.debug("AsyncAgentWebSocketClient._process_binary ENTER")
        self._logger.debug("Binary data received")

        await self._emit(
            AgentWebSocketEvents(AgentWebSocketEvents.AudioData),
            data=message,
            **dict(cast(Dict[Any, Any], self._kwargs)),
        )

        self._logger.notice("_process_binary Succeeded")
        self._logger.debug("AsyncAgentWebSocketClient._process_binary LEAVE")

    # pylint: disable=too-many-return-statements
    async def _keep_alive(self) -> None:
        """
        Sends keepalive messages to the WebSocket connection.
        """
        self._logger.debug("AsyncAgentWebSocketClient._keep_alive ENTER")

        counter = 0
        while True:
            try:
                counter += 1
                await asyncio.sleep(ONE_SECOND)

                if self._exit_event.is_set():
                    self._logger.notice("_keep_alive exiting gracefully")
                    self._logger.debug("AsyncAgentWebSocketClient._keep_alive LEAVE")
                    return

                # deepgram keepalive
                if counter % DEEPGRAM_INTERVAL == 0:
                    await self.keep_alive()

            except Exception as e:  # pylint: disable=broad-except
                self._logger.error(
                    "Exception in AsyncAgentWebSocketClient._keep_alive: %s", e
                )
                e_error: ErrorResponse = ErrorResponse(
                    "Exception in AsyncAgentWebSocketClient._keep_alive",
                    f"{e}",
                    "Exception",
                )
                self._logger.error(
                    "Exception in AsyncAgentWebSocketClient._keep_alive: %s", str(e)
                )
                await self._emit(
                    AgentWebSocketEvents(AgentWebSocketEvents.Error),
                    error=e_error,
                    **dict(cast(Dict[Any, Any], self._kwargs)),
                )

                # signal exit and close
                await super()._signal_exit()

                self._logger.debug("AsyncAgentWebSocketClient._keep_alive LEAVE")

                if self._config.options.get("termination_exception") is True:
                    raise
                return

    async def keep_alive(self) -> bool:
        """
        Sends a KeepAlive message
        """
        self._logger.spam("AsyncAgentWebSocketClient.keep_alive ENTER")

        self._logger.notice("Sending KeepAlive...")
        ret = await self.send(json.dumps({"type": "KeepAlive"}))

        if not ret:
            self._logger.error("keep_alive failed")
            self._logger.spam("AsyncAgentWebSocketClient.keep_alive LEAVE")
            return False

        self._logger.notice("keep_alive succeeded")
        self._logger.spam("AsyncAgentWebSocketClient.keep_alive LEAVE")

        return True

    async def _close_message(self) -> bool:
        # TODO: No known API close message # pylint: disable=fixme
        # return await self.send(json.dumps({"type": "Close"}))
        return True

    async def finish(self) -> bool:
        """
        Closes the WebSocket connection gracefully.
        """
        self._logger.debug("AsyncAgentWebSocketClient.finish ENTER")

        # stop the threads
        self._logger.verbose("cancelling tasks...")
        try:
            # call parent finish
            if await super().finish() is False:
                self._logger.error("AsyncAgentWebSocketClient.finish failed")

            if self._microphone is not None and self._microphone_created:
                self._microphone.finish()
                self._microphone_created = False

            if self._speaker is not None and self._speaker_created:
                self._speaker.finish()
                self._speaker_created = False

            # Before cancelling, check if the tasks were created
            # debug the threads
            for thread in threading.enumerate():
                self._logger.debug("before running thread: %s", thread.name)
            self._logger.debug("number of active threads: %s", threading.active_count())

            tasks = []
            if self._keep_alive_thread is not None:
                self._keep_alive_thread.cancel()
                tasks.append(self._keep_alive_thread)
                self._logger.notice("processing _keep_alive_thread cancel...")

            # Use asyncio.gather to wait for tasks to be cancelled
            # Prevent indefinite waiting by setting a timeout
            await asyncio.wait_for(asyncio.gather(*tasks), timeout=10)
            self._logger.notice("threads joined")

            self._speaker = None
            self._microphone = None

            # debug the threads
            for thread in threading.enumerate():
                self._logger.debug("after running thread: %s", thread.name)
            self._logger.debug("number of active threads: %s", threading.active_count())

            self._logger.notice("finish succeeded")
            self._logger.spam("AsyncAgentWebSocketClient.finish LEAVE")
            return True

        except asyncio.CancelledError as e:
            self._logger.error("tasks cancelled error: %s", e)
            self._logger.debug("AsyncAgentWebSocketClient.finish LEAVE")
            return False

        except asyncio.TimeoutError as e:
            self._logger.error("tasks cancellation timed out: %s", e)
            self._logger.debug("AsyncAgentWebSocketClient.finish LEAVE")
            return False


================================================
File: deepgram/clients/agent/v1/websocket/client.py
================================================
# Copyright 2024 Deepgram SDK contributors. All Rights Reserved.
# Use of this source code is governed by a MIT license that can be found in the LICENSE file.
# SPDX-License-Identifier: MIT

import json
import logging
from typing import Dict, Union, Optional, cast, Any, Callable
import threading
import time

from .....utils import verboselogs
from .....options import DeepgramClientOptions
from ...enums import AgentWebSocketEvents
from ....common import AbstractSyncWebSocketClient
from ....common import DeepgramError

from .response import (
    OpenResponse,
    WelcomeResponse,
    SettingsAppliedResponse,
    ConversationTextResponse,
    UserStartedSpeakingResponse,
    AgentThinkingResponse,
    FunctionCalling,
    FunctionCallRequest,
    AgentStartedSpeakingResponse,
    AgentAudioDoneResponse,
    InjectionRefusedResponse,
    CloseResponse,
    ErrorResponse,
    UnhandledResponse,
)
from .options import (
    SettingsConfigurationOptions,
    UpdateInstructionsOptions,
    UpdateSpeakOptions,
    InjectAgentMessageOptions,
    FunctionCallResponse,
    AgentKeepAlive,
)

from .....audio.speaker import (
    Speaker,
    RATE as SPEAKER_RATE,
    CHANNELS as SPEAKER_CHANNELS,
    PLAYBACK_DELTA as SPEAKER_PLAYBACK_DELTA,
)
from .....audio.microphone import (
    Microphone,
    RATE as MICROPHONE_RATE,
    CHANNELS as MICROPHONE_CHANNELS,
)

ONE_SECOND = 1
HALF_SECOND = 0.5
DEEPGRAM_INTERVAL = 5


class AgentWebSocketClient(
    AbstractSyncWebSocketClient
):  # pylint: disable=too-many-instance-attributes
    """
    Client for interacting with Deepgram's live transcription services over WebSockets.

     This class provides methods to establish a WebSocket connection for live transcription and handle real-time transcription events.

     Args:
         config (DeepgramClientOptions): all the options for the client.
    """

    _logger: verboselogs.VerboseLogger
    _config: DeepgramClientOptions
    _endpoint: str

    _event_handlers: Dict[AgentWebSocketEvents, list]

    _keep_alive_thread: Union[threading.Thread, None]

    _kwargs: Optional[Dict] = None
    _addons: Optional[Dict] = None
    # note the distinction here. We can't use _config because it's already used in the parent
    _settings: Optional[SettingsConfigurationOptions] = None
    _headers: Optional[Dict] = None

    _speaker_created: bool = False
    _speaker: Optional[Speaker] = None
    _microphone_created: bool = False
    _microphone: Optional[Microphone] = None

    def __init__(self, config: DeepgramClientOptions):
        if config is None:
            raise DeepgramError("Config is required")

        self._logger = verboselogs.VerboseLogger(__name__)
        self._logger.addHandler(logging.StreamHandler())
        self._logger.setLevel(config.verbose)

        self._config = config

        # needs to be "wss://agent.deepgram.com/agent"
        self._endpoint = "agent"

        # override the endpoint since it needs to be "wss://agent.deepgram.com/agent"
        self._config.url = "agent.deepgram.com"

        self._keep_alive_thread = None

        # init handlers
        self._event_handlers = {
            event: [] for event in AgentWebSocketEvents.__members__.values()
        }

        if self._config.options.get("microphone_record") == "true":
            self._logger.info("microphone_record is enabled")
            rate = self._config.options.get("microphone_record_rate", MICROPHONE_RATE)
            channels = self._config.options.get(
                "microphone_record_channels", MICROPHONE_CHANNELS
            )
            device_index = self._config.options.get("microphone_record_device_index")

            self._logger.debug("rate: %s", rate)
            self._logger.debug("channels: %s", channels)

            self._microphone_created = True

            if device_index is not None:
                self._logger.debug("device_index: %s", device_index)
                self._microphone = Microphone(
                    rate=rate,
                    channels=channels,
                    verbose=self._config.verbose,
                    input_device_index=device_index,
                )
            else:
                self._microphone = Microphone(
                    rate=rate,
                    channels=channels,
                    verbose=self._config.verbose,
                )

        if self._config.options.get("speaker_playback") == "true":
            self._logger.info("speaker_playback is enabled")
            rate = self._config.options.get("speaker_playback_rate", SPEAKER_RATE)
            channels = self._config.options.get(
                "speaker_playback_channels", SPEAKER_CHANNELS
            )
            playback_delta_in_ms = self._config.options.get(
                "speaker_playback_delta_in_ms", SPEAKER_PLAYBACK_DELTA
            )
            device_index = self._config.options.get("speaker_playback_device_index")

            self._logger.debug("rate: %s", rate)
            self._logger.debug("channels: %s", channels)

            self._speaker_created = True

            if device_index is not None:
                self._logger.debug("device_index: %s", device_index)

                self._speaker = Speaker(
                    rate=rate,
                    channels=channels,
                    last_play_delta_in_ms=playback_delta_in_ms,
                    verbose=self._config.verbose,
                    output_device_index=device_index,
                    microphone=self._microphone,
                )
            else:
                self._speaker = Speaker(
                    rate=rate,
                    channels=channels,
                    last_play_delta_in_ms=playback_delta_in_ms,
                    verbose=self._config.verbose,
                    microphone=self._microphone,
                )

        # call the parent constructor
        super().__init__(self._config, self._endpoint)

    # pylint: disable=too-many-statements,too-many-branches
    def start(
        self,
        options: Optional[SettingsConfigurationOptions] = None,
        addons: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        members: Optional[Dict] = None,
        **kwargs,
    ) -> bool:
        """
        Starts the WebSocket connection for agent API.
        """
        self._logger.debug("AgentWebSocketClient.start ENTER")
        self._logger.info("settings: %s", options)
        self._logger.info("addons: %s", addons)
        self._logger.info("headers: %s", headers)
        self._logger.info("members: %s", members)
        self._logger.info("kwargs: %s", kwargs)

        if isinstance(options, SettingsConfigurationOptions) and not options.check():
            self._logger.error("settings.check failed")
            self._logger.debug("AgentWebSocketClient.start LEAVE")
            raise DeepgramError("Fatal agent settings error")

        self._addons = addons
        self._headers = headers

        # add "members" as members of the class
        if members is not None:
            self.__dict__.update(members)

        # set kwargs as members of the class
        if kwargs is not None:
            self._kwargs = kwargs
        else:
            self._kwargs = {}

        if isinstance(options, SettingsConfigurationOptions):
            self._logger.info("options is class")
            self._settings = options
        elif isinstance(options, dict):
            self._logger.info("options is dict")
            self._settings = SettingsConfigurationOptions.from_dict(options)
        elif isinstance(options, str):
            self._logger.info("options is json")
            self._settings = SettingsConfigurationOptions.from_json(options)
        else:
            raise DeepgramError("Invalid options type")

        try:
            # speaker substitutes the listening thread
            if self._speaker is not None:
                self._logger.notice("passing speaker to delegate_listening")
                super().delegate_listening(self._speaker)

            # call parent start
            if (
                super().start(
                    {},
                    self._addons,
                    self._headers,
                    **dict(cast(Dict[Any, Any], self._kwargs)),
                )
                is False
            ):
                self._logger.error("AgentWebSocketClient.start failed")
                self._logger.debug("AgentWebSocketClient.start LEAVE")
                return False

            if self._speaker is not None:
                self._logger.notice("speaker is delegate_listening. Starting speaker")
                self._speaker.start()

            if self._speaker is not None and self._microphone is not None:
                self._logger.notice(
                    "speaker is delegate_listening. Starting microphone"
                )
                self._microphone.set_callback(self.send)
                self._microphone.start()

            # debug the threads
            for thread in threading.enumerate():
                self._logger.debug("after running thread: %s", thread.name)
            self._logger.debug("number of active threads: %s", threading.active_count())

            # keepalive thread
            if self._config.is_keep_alive_enabled():
                self._logger.notice("keepalive is enabled")
                self._keep_alive_thread = threading.Thread(target=self._keep_alive)
                self._keep_alive_thread.start()
            else:
                self._logger.notice("keepalive is disabled")

            # debug the threads
            for thread in threading.enumerate():
                self._logger.debug("after running thread: %s", thread.name)
            self._logger.debug("number of active threads: %s", threading.active_count())

            # send the configurationsetting message
            self._logger.notice("Sending ConfigurationSettings...")
            ret_send_cs = self.send(str(self._settings))
            if not ret_send_cs:
                self._logger.error("ConfigurationSettings failed")

                err_error: ErrorResponse = ErrorResponse(
                    "Exception in AgentWebSocketClient.start",
                    "ConfigurationSettings failed to send",
                    "Exception",
                )
                self._emit(
                    AgentWebSocketEvents(AgentWebSocketEvents.Error),
                    error=err_error,
                    **dict(cast(Dict[Any, Any], self._kwargs)),
                )

                self._logger.debug("AgentWebSocketClient.start LEAVE")
                return False

            self._logger.notice("start succeeded")
            self._logger.debug("AgentWebSocketClient.start LEAVE")
            return True

        except Exception as e:  # pylint: disable=broad-except
            self._logger.error(
                "WebSocketException in AgentWebSocketClient.start: %s", e
            )
            self._logger.debug("AgentWebSocketClient.start LEAVE")
            if self._config.options.get("termination_exception_connect") is True:
                raise e
            return False

    # pylint: enable=too-many-statements,too-many-branches

    def on(self, event: AgentWebSocketEvents, handler: Callable) -> None:
        """
        Registers event handlers for specific events.
        """
        self._logger.info("event subscribed: %s", event)
        if event in AgentWebSocketEvents.__members__.values() and callable(handler):
            self._event_handlers[event].append(handler)

    def _emit(self, event: AgentWebSocketEvents, *args, **kwargs) -> None:
        """
        Emits events to the registered event handlers.
        """
        self._logger.debug("AgentWebSocketClient._emit ENTER")
        self._logger.debug("callback handlers for: %s", event)

        # debug the threads
        for thread in threading.enumerate():
            self._logger.debug("after running thread: %s", thread.name)
        self._logger.debug("number of active threads: %s", threading.active_count())

        self._logger.debug("callback handlers for: %s", event)
        for handler in self._event_handlers[event]:
            handler(self, *args, **kwargs)

        # debug the threads
        for thread in threading.enumerate():
            self._logger.debug("after running thread: %s", thread.name)
        self._logger.debug("number of active threads: %s", threading.active_count())

        self._logger.debug("AgentWebSocketClient._emit LEAVE")

    # pylint: disable=too-many-return-statements,too-many-statements,too-many-locals,too-many-branches
    def _process_text(self, message: str) -> None:
        """
        Processes messages received over the WebSocket connection.
        """
        self._logger.debug("AgentWebSocketClient._process_text ENTER")

        try:
            self._logger.debug("Text data received")
            if len(message) == 0:
                self._logger.debug("message is empty")
                self._logger.debug("AgentWebSocketClient._process_text LEAVE")
                return

            data = json.loads(message)
            response_type = data.get("type")
            self._logger.debug("response_type: %s, data: %s", response_type, data)

            match response_type:
                case AgentWebSocketEvents.Open:
                    open_result: OpenResponse = OpenResponse.from_json(message)
                    self._logger.verbose("OpenResponse: %s", open_result)
                    self._emit(
                        AgentWebSocketEvents(AgentWebSocketEvents.Open),
                        open=open_result,
                        **dict(cast(Dict[Any, Any], self._kwargs)),
                    )
                case AgentWebSocketEvents.Welcome:
                    welcome_result: WelcomeResponse = WelcomeResponse.from_json(message)
                    self._logger.verbose("WelcomeResponse: %s", welcome_result)
                    self._emit(
                        AgentWebSocketEvents(AgentWebSocketEvents.Welcome),
                        welcome=welcome_result,
                        **dict(cast(Dict[Any, Any], self._kwargs)),
                    )
                case AgentWebSocketEvents.SettingsApplied:
                    settings_applied_result: SettingsAppliedResponse = (
                        SettingsAppliedResponse.from_json(message)
                    )
                    self._logger.verbose(
                        "SettingsAppliedResponse: %s", settings_applied_result
                    )
                    self._emit(
                        AgentWebSocketEvents(AgentWebSocketEvents.SettingsApplied),
                        settings_applied=settings_applied_result,
                        **dict(cast(Dict[Any, Any], self._kwargs)),
                    )
                case AgentWebSocketEvents.ConversationText:
                    conversation_text_result: ConversationTextResponse = (
                        ConversationTextResponse.from_json(message)
                    )
                    self._logger.verbose(
                        "ConversationTextResponse: %s", conversation_text_result
                    )
                    self._emit(
                        AgentWebSocketEvents(AgentWebSocketEvents.ConversationText),
                        conversation_text=conversation_text_result,
                        **dict(cast(Dict[Any, Any], self._kwargs)),
                    )
                case AgentWebSocketEvents.UserStartedSpeaking:
                    user_started_speaking_result: UserStartedSpeakingResponse = (
                        UserStartedSpeakingResponse.from_json(message)
                    )
                    self._logger.verbose(
                        "UserStartedSpeakingResponse: %s", user_started_speaking_result
                    )
                    self._emit(
                        AgentWebSocketEvents(AgentWebSocketEvents.UserStartedSpeaking),
                        user_started_speaking=user_started_speaking_result,
                        **dict(cast(Dict[Any, Any], self._kwargs)),
                    )
                case AgentWebSocketEvents.AgentThinking:
                    agent_thinking_result: AgentThinkingResponse = (
                        AgentThinkingResponse.from_json(message)
                    )
                    self._logger.verbose(
                        "AgentThinkingResponse: %s", agent_thinking_result
                    )
                    self._emit(
                        AgentWebSocketEvents(AgentWebSocketEvents.AgentThinking),
                        agent_thinking=agent_thinking_result,
                        **dict(cast(Dict[Any, Any], self._kwargs)),
                    )
                case AgentWebSocketEvents.FunctionCalling:
                    function_calling_result: FunctionCalling = (
                        FunctionCalling.from_json(message)
                    )
                    self._logger.verbose("FunctionCalling: %s", function_calling_result)
                    self._emit(
                        AgentWebSocketEvents(AgentWebSocketEvents.FunctionCalling),
                        function_calling=function_calling_result,
                        **dict(cast(Dict[Any, Any], self._kwargs)),
                    )
                case AgentWebSocketEvents.FunctionCallRequest:
                    function_call_request_result: FunctionCallRequest = (
                        FunctionCallRequest.from_json(message)
                    )
                    self._logger.verbose(
                        "FunctionCallRequest: %s", function_call_request_result
                    )
                    self._emit(
                        AgentWebSocketEvents(AgentWebSocketEvents.FunctionCallRequest),
                        function_call_request=function_call_request_result,
                        **dict(cast(Dict[Any, Any], self._kwargs)),
                    )
                case AgentWebSocketEvents.AgentStartedSpeaking:
                    agent_started_speaking_result: AgentStartedSpeakingResponse = (
                        AgentStartedSpeakingResponse.from_json(message)
                    )
                    self._logger.verbose(
                        "AgentStartedSpeakingResponse: %s",
                        agent_started_speaking_result,
                    )
                    self._emit(
                        AgentWebSocketEvents(AgentWebSocketEvents.AgentStartedSpeaking),
                        agent_started_speaking=agent_started_speaking_result,
                        **dict(cast(Dict[Any, Any], self._kwargs)),
                    )
                case AgentWebSocketEvents.AgentAudioDone:
                    agent_audio_done_result: AgentAudioDoneResponse = (
                        AgentAudioDoneResponse.from_json(message)
                    )
                    self._logger.verbose(
                        "AgentAudioDoneResponse: %s", agent_audio_done_result
                    )
                    self._emit(
                        AgentWebSocketEvents(AgentWebSocketEvents.AgentAudioDone),
                        agent_audio_done=agent_audio_done_result,
                        **dict(cast(Dict[Any, Any], self._kwargs)),
                    )
                case AgentWebSocketEvents.InjectionRefused:
                    injection_refused_result: InjectionRefusedResponse = (
                        InjectionRefusedResponse.from_json(message)
                    )
                    self._logger.verbose(
                        "InjectionRefused: %s", injection_refused_result
                    )
                    self._emit(
                        AgentWebSocketEvents(AgentWebSocketEvents.InjectionRefused),
                        injection_refused=injection_refused_result,
                        **dict(cast(Dict[Any, Any], self._kwargs)),
                    )
                case AgentWebSocketEvents.Close:
                    close_result: CloseResponse = CloseResponse.from_json(message)
                    self._logger.verbose("CloseResponse: %s", close_result)
                    self._emit(
                        AgentWebSocketEvents(AgentWebSocketEvents.Close),
                        close=close_result,
                        **dict(cast(Dict[Any, Any], self._kwargs)),
                    )
                case AgentWebSocketEvents.Error:
                    err_error: ErrorResponse = ErrorResponse.from_json(message)
                    self._logger.verbose("ErrorResponse: %s", err_error)
                    self._emit(
                        AgentWebSocketEvents(AgentWebSocketEvents.Error),
                        error=err_error,
                        **dict(cast(Dict[Any, Any], self._kwargs)),
                    )
                case _:
                    self._logger.warning(
                        "Unknown Message: response_type: %s, data: %s",
                        response_type,
                        data,
                    )
                    unhandled_error: UnhandledResponse = UnhandledResponse(
                        type=AgentWebSocketEvents(AgentWebSocketEvents.Unhandled),
                        raw=message,
                    )
                    self._emit(
                        AgentWebSocketEvents(AgentWebSocketEvents.Unhandled),
                        unhandled=unhandled_error,
                        **dict(cast(Dict[Any, Any], self._kwargs)),
                    )

            self._logger.notice("_process_text Succeeded")
            self._logger.debug("SpeakStreamClient._process_text LEAVE")

        except Exception as e:  # pylint: disable=broad-except
            self._logger.error("Exception in AgentWebSocketClient._process_text: %s", e)
            e_error: ErrorResponse = ErrorResponse(
                "Exception in AgentWebSocketClient._process_text",
                f"{e}",
                "Exception",
            )
            self._logger.error(
                "Exception in AgentWebSocketClient._process_text: %s", str(e)
            )
            self._emit(
                AgentWebSocketEvents(AgentWebSocketEvents.Error),
                error=e_error,
                **dict(cast(Dict[Any, Any], self._kwargs)),
            )

            # signal exit and close
            super()._signal_exit()

            self._logger.debug("AgentWebSocketClient._process_text LEAVE")

            if self._config.options.get("termination_exception") is True:
                raise
            return

    # pylint: enable=too-many-return-statements,too-many-statements

    def _process_binary(self, message: bytes) -> None:
        self._logger.debug("AgentWebSocketClient._process_binary ENTER")
        self._logger.debug("Binary data received")

        self._emit(
            AgentWebSocketEvents(AgentWebSocketEvents.AudioData),
            data=message,
            **dict(cast(Dict[Any, Any], self._kwargs)),
        )

        self._logger.notice("_process_binary Succeeded")
        self._logger.debug("AgentWebSocketClient._process_binary LEAVE")

    # pylint: disable=too-many-return-statements
    def _keep_alive(self) -> None:
        """
        Sends keepalive messages to the WebSocket connection.
        """
        self._logger.debug("AgentWebSocketClient._keep_alive ENTER")

        counter = 0
        while True:
            try:
                counter += 1
                self._exit_event.wait(timeout=ONE_SECOND)

                if self._exit_event.is_set():
                    self._logger.notice("_keep_alive exiting gracefully")
                    self._logger.debug("AgentWebSocketClient._keep_alive LEAVE")
                    return

                # deepgram keepalive
                if counter % DEEPGRAM_INTERVAL == 0:
                    self.keep_alive()

            except Exception as e:  # pylint: disable=broad-except
                self._logger.error(
                    "Exception in AgentWebSocketClient._keep_alive: %s", e
                )
                e_error: ErrorResponse = ErrorResponse(
                    "Exception in AgentWebSocketClient._keep_alive",
                    f"{e}",
                    "Exception",
                )
                self._logger.error(
                    "Exception in AgentWebSocketClient._keep_alive: %s", str(e)
                )
                self._emit(
                    AgentWebSocketEvents(AgentWebSocketEvents.Error),
                    error=e_error,
                    **dict(cast(Dict[Any, Any], self._kwargs)),
                )

                # signal exit and close
                super()._signal_exit()

                self._logger.debug("AgentWebSocketClient._keep_alive LEAVE")

                if self._config.options.get("termination_exception") is True:
                    raise
                return

    def keep_alive(self) -> bool:
        """
        Sends a KeepAlive message
        """
        self._logger.spam("AgentWebSocketClient.keep_alive ENTER")

        self._logger.notice("Sending KeepAlive...")
        ret = self.send(json.dumps({"type": "KeepAlive"}))

        if not ret:
            self._logger.error("keep_alive failed")
            self._logger.spam("AgentWebSocketClient.keep_alive LEAVE")
            return False

        self._logger.notice("keep_alive succeeded")
        self._logger.spam("AgentWebSocketClient.keep_alive LEAVE")

        return True

    def _close_message(self) -> bool:
        # TODO: No known API close message # pylint: disable=fixme
        # return self.send(json.dumps({"type": "Close"}))
        return True

    # closes the WebSocket connection gracefully
    def finish(self) -> bool:
        """
        Closes the WebSocket connection gracefully.
        """
        self._logger.spam("AgentWebSocketClient.finish ENTER")

        # call parent finish
        if super().finish() is False:
            self._logger.error("AgentWebSocketClient.finish failed")

        if self._microphone is not None and self._microphone_created:
            self._microphone.finish()
            self._microphone_created = False

        if self._speaker is not None and self._speaker_created:
            self._speaker.finish()
            self._speaker_created = False

        # debug the threads
        for thread in threading.enumerate():
            self._logger.debug("before running thread: %s", thread.name)
        self._logger.debug("number of active threads: %s", threading.active_count())

        # stop the threads
        self._logger.verbose("cancelling tasks...")
        if self._keep_alive_thread is not None:
            self._keep_alive_thread.join()
            self._keep_alive_thread = None
            self._logger.notice("processing _keep_alive_thread thread joined")

        if self._listen_thread is not None:
            self._listen_thread.join()
            self._listen_thread = None
        self._logger.notice("listening thread joined")

        self._speaker = None
        self._microphone = None

        # debug the threads
        for thread in threading.enumerate():
            self._logger.debug("before running thread: %s", thread.name)
        self._logger.debug("number of active threads: %s", threading.active_count())

        self._logger.notice("finish succeeded")
        self._logger.spam("AgentWebSocketClient.finish LEAVE")
        return True


================================================
File: deepgram/clients/agent/v1/websocket/options.py
================================================
# Copyright 2024 Deepgram SDK contributors. All Rights Reserved.
# Use of this source code is governed by a MIT license that can be found in the LICENSE file.
# SPDX-License-Identifier: MIT

from typing import List, Optional, Union, Any, Tuple
import logging

from dataclasses import dataclass, field
from dataclasses_json import config as dataclass_config

from deepgram.utils import verboselogs

from ...enums import AgentWebSocketEvents
from ....common import BaseResponse


# ConfigurationSettings


@dataclass
class Listen(BaseResponse):
    """
    This class defines any configuration settings for the Listen model.
    """

    model: Optional[str] = field(
        default=None, metadata=dataclass_config(exclude=lambda f: f is None)
    )


@dataclass
class Speak(BaseResponse):
    """
    This class defines any configuration settings for the Speak model.
    """

    model: Optional[str] = field(
        default="aura-asteria-en",
        metadata=dataclass_config(exclude=lambda f: f is None),
    )
    provider: Optional[str] = field(
        default=None, metadata=dataclass_config(exclude=lambda f: f is None)
    )
    voice_id: Optional[str] = field(
        default=None, metadata=dataclass_config(exclude=lambda f: f is None)
    )


@dataclass
class Header(BaseResponse):
    """
    This class defines a single key/value pair for a header.
    """

    key: str
    value: str


@dataclass
class Item(BaseResponse):
    """
    This class defines a single item in a list of items.
    """

    type: str
    description: str


@dataclass
class Properties(BaseResponse):
    """
    This class defines the properties which is just a list of items.
    """

    item: Item

    def __getitem__(self, key):
        _dict = self.to_dict()
        if "item" in _dict:
            _dict["item"] = [Item.from_dict(item) for item in _dict["item"]]
        return _dict[key]


@dataclass
class Parameters(BaseResponse):
    """
    This class defines the parameters for a function.
    """

    type: str
    properties: Properties
    required: List[str]

    def __getitem__(self, key):
        _dict = self.to_dict()
        if "properties" in _dict:
            _dict["properties"] = _dict["properties"].copy()
        return _dict[key]


@dataclass
class Function(BaseResponse):
    """
    This class defines a function for the Think model.
    """

    name: str
    description: str
    url: str
    method: str
    headers: Optional[List[Header]] = field(
        default=None, metadata=dataclass_config(exclude=lambda f: f is None)
    )
    parameters: Optional[Parameters] = field(
        default=None, metadata=dataclass_config(exclude=lambda f: f is None)
    )

    def __getitem__(self, key):
        _dict = self.to_dict()
        if "parameters" in _dict:
            _dict["parameters"] = [
                Parameters.from_dict(parameters) for parameters in _dict["parameters"]
            ]
        if "headers" in _dict:
            _dict["headers"] = [
                Header.from_dict(headers) for headers in _dict["headers"]
            ]
        return _dict[key]


@dataclass
class Provider(BaseResponse):
    """
    This class defines the provider for the Think model.
    """

    type: Optional[str] = field(
        default=None, metadata=dataclass_config(exclude=lambda f: f is None)
    )


@dataclass
class Think(BaseResponse):
    """
    This class defines any configuration settings for the Think model.
    """

    provider: Provider = field(default_factory=Provider)
    model: Optional[str] = field(
        default=None, metadata=dataclass_config(exclude=lambda f: f is None)
    )
    instructions: Optional[str] = field(
        default=None, metadata=dataclass_config(exclude=lambda f: f is None)
    )
    functions: Optional[List[Function]] = field(
        default=None, metadata=dataclass_config(exclude=lambda f: f is None)
    )

    def __getitem__(self, key):
        _dict = self.to_dict()
        if "provider" in _dict:
            _dict["provider"] = [
                Provider.from_dict(provider) for provider in _dict["provider"]
            ]
        if "functions" in _dict:
            _dict["functions"] = [
                Function.from_dict(functions) for functions in _dict["functions"]
            ]
        return _dict[key]


@dataclass
class Agent(BaseResponse):
    """
    This class defines any configuration settings for the Agent model.
    """

    listen: Listen = field(default_factory=Listen)
    think: Think = field(default_factory=Think)
    speak: Speak = field(default_factory=Speak)

    def __getitem__(self, key):
        _dict = self.to_dict()
        if "listen" in _dict:
            _dict["listen"] = [Listen.from_dict(listen) for listen in _dict["listen"]]
        if "think" in _dict:
            _dict["think"] = [Think.from_dict(think) for think in _dict["think"]]
        if "speak" in _dict:
            _dict["speak"] = [Speak.from_dict(speak) for speak in _dict["speak"]]
        return _dict[key]


@dataclass
class Input(BaseResponse):
    """
    This class defines any configuration settings for the input audio.
    """

    encoding: Optional[str] = field(default="linear16")
    sample_rate: int = field(default=16000)


@dataclass
class Output(BaseResponse):
    """
    This class defines any configuration settings for the output audio.
    """

    encoding: Optional[str] = field(default="linear16")
    sample_rate: Optional[int] = field(default=16000)
    bitrate: Optional[int] = field(
        default=None, metadata=dataclass_config(exclude=lambda f: f is None)
    )
    container: Optional[str] = field(default="none")


@dataclass
class Audio(BaseResponse):
    """
    This class defines any configuration settings for the audio.
    """

    input: Optional[Input] = field(default_factory=Input)
    output: Optional[Output] = field(default_factory=Output)

    def __getitem__(self, key):
        _dict = self.to_dict()
        if "input" in _dict:
            _dict["input"] = [Input.from_dict(input) for input in _dict["input"]]
        if "output" in _dict:
            _dict["output"] = [Output.from_dict(output) for output in _dict["output"]]
        return _dict[key]


@dataclass
class Context(BaseResponse):
    """
    This class defines any configuration settings for the context.
    """

    messages: Optional[List[Tuple[str, str]]] = field(
        default=None, metadata=dataclass_config(exclude=lambda f: f is None)
    )
    replay: Optional[bool] = field(default=False)

    def __getitem__(self, key):
        _dict = self.to_dict()
        if "messages" in _dict:
            _dict["messages"] = _dict["messages"].copy()
        return _dict[key]


@dataclass
class SettingsConfigurationOptions(BaseResponse):
    """
    The client should send a SettingsConfiguration message immediately after opening the websocket and before sending any audio.
    """

    type: str = str(AgentWebSocketEvents.SettingsConfiguration)
    audio: Audio = field(default_factory=Audio)
    agent: Agent = field(default_factory=Agent)
    context: Optional[Context] = field(
        default=None, metadata=dataclass_config(exclude=lambda f: f is None)
    )

    def __getitem__(self, key):
        _dict = self.to_dict()
        if "audio" in _dict:
            _dict["audio"] = [Audio.from_dict(audio) for audio in _dict["audio"]]
        if "agent" in _dict:
            _dict["agent"] = [Agent.from_dict(agent) for agent in _dict["agent"]]
        if "context" in _dict:
            _dict["context"] = [
                Context.from_dict(context) for context in _dict["context"]
            ]
        return _dict[key]

    def check(self):
        """
        Check the options for any deprecated or soon-to-be-deprecated options.
        """
        logger = verboselogs.VerboseLogger(__name__)
        logger.addHandler(logging.StreamHandler())
        prev = logger.level
        logger.setLevel(verboselogs.ERROR)

        # do we need to check anything here?

        logger.setLevel(prev)

        return True


# UpdateInstructions


@dataclass
class UpdateInstructionsOptions(BaseResponse):
    """
    The client can send an UpdateInstructions message to give additional instructions to the Think model in the middle of a conversation.
    """

    type: str = str(AgentWebSocketEvents.UpdateInstructions)
    instructions: str = field(default="")


# UpdateSpeak


@dataclass
class UpdateSpeakOptions(BaseResponse):
    """
    The client can send an UpdateSpeak message to change the Speak model in the middle of a conversation.
    """

    type: str = str(AgentWebSocketEvents.UpdateSpeak)
    model: str = field(default="")


# InjectAgentMessage


@dataclass
class InjectAgentMessageOptions(BaseResponse):
    """
    The client can send an InjectAgentMessage to immediately trigger an agent statement. If the injection request arrives while the user is speaking, or while the server is in the middle of sending audio for an agent response, then the request will be ignored and the server will reply with an InjectionRefused.
    """

    type: str = str(AgentWebSocketEvents.InjectAgentMessage)
    message: str = field(default="")


# Function Call Response


@dataclass
class FunctionCallResponse(BaseResponse):
    """
    TheFunctionCallResponse message is a JSON command that the client should reply with every time there is a FunctionCallRequest received.
    """

    type: str = "FunctionCallResponse"
    function_call_id: str = field(default="")
    output: str = field(default="")


# Agent Keep Alive


@dataclass
class AgentKeepAlive(BaseResponse):
    """
    The KeepAlive message is a JSON command that you can use to ensure that the server does not close the connection.
    """

    type: str = "KeepAlive"


================================================
File: deepgram/clients/agent/v1/websocket/response.py
================================================
# Copyright 2023-2024 Deepgram SDK contributors. All Rights Reserved.
# Use of this source code is governed by a MIT license that can be found in the LICENSE file.
# SPDX-License-Identifier: MIT

from typing import List, Optional, Dict, Any

from dataclasses import dataclass

# common websocket response
from ....common import (
    BaseResponse,
    OpenResponse,
    CloseResponse,
    ErrorResponse,
    UnhandledResponse,
)

# unique


@dataclass
class WelcomeResponse(BaseResponse):
    """
    The server will send a Welcome message as soon as the websocket opens.
    """

    type: str
    session_id: str


@dataclass
class SettingsAppliedResponse(BaseResponse):
    """
    The server will send a SettingsApplied message as soon as the settings are applied.
    """

    type: str


@dataclass
class ConversationTextResponse(BaseResponse):
    """
    The server will send a ConversationText message every time the agent hears the user say something, and every time the agent speaks something itself.
    """

    type: str
    role: str
    content: str


@dataclass
class UserStartedSpeakingResponse(BaseResponse):
    """
    The server will send a UserStartedSpeaking message every time the user begins a new utterance.
    """

    type: str


@dataclass
class AgentThinkingResponse(BaseResponse):
    """
    The server will send an AgentThinking message to inform the client of a non-verbalized agent thought.
    """

    type: str
    content: str


@dataclass
class FunctionCalling(BaseResponse):
    """
    The server will sometimes send FunctionCalling messages when making function calls to help the client developer debug function calling workflows.
    """

    type: str


@dataclass
class FunctionCallRequest(BaseResponse):
    """
    The FunctionCallRequest message is used to call a function from the server to the client.
    """

    type: str
    function_name: str
    function_call_id: str
    input: str


@dataclass
class AgentStartedSpeakingResponse(BaseResponse):
    """
    The server will send an AgentStartedSpeaking message when it begins streaming an agent audio response to the client for playback.
    """

    total_latency: float
    tts_latency: float
    ttt_latency: float


@dataclass
class AgentAudioDoneResponse(BaseResponse):
    """
    The server will send an AgentAudioDone message immediately after it sends the last audio message in a piece of agent speech.
    """

    type: str


@dataclass
class InjectionRefusedResponse(BaseResponse):
    """
    The server will send an InjectionRefused message when an InjectAgentMessage request is ignored because it arrived while the user was speaking or while the server was sending audio for an agent response.
    """

    type: str


================================================
File: deepgram/clients/analyze/__init__.py
================================================
# Copyright 2023-2024 Deepgram SDK contributors. All Rights Reserved.
# Use of this source code is governed by a MIT license that can be found in the LICENSE file.
# SPDX-License-Identifier: MIT

from .client import AnalyzeClient, AsyncAnalyzeClient
from .client import ReadClient, AsyncReadClient
from .client import AnalyzeOptions
from .client import (
    # common
    UrlSource,
    TextSource,
    BufferSource,
    StreamSource,
    FileSource,
    # unique
    AnalyzeStreamSource,
    AnalyzeSource,
)
from .client import (
    AsyncAnalyzeResponse,
    SyncAnalyzeResponse,
    AnalyzeResponse,
    # shared
    Average,
    Intent,
    Intents,
    IntentsInfo,
    Segment,
    SentimentInfo,
    Sentiment,
    Sentiments,
    SummaryInfo,
    Topic,
    Topics,
    TopicsInfo,
    # unique
    AnalyzeMetadata,
    AnalyzeResults,
    AnalyzeSummary,
)


================================================
File: deepgram/clients/analyze/client.py
================================================
# Copyright 2024 Deepgram SDK contributors. All Rights Reserved.
# Use of this source code is governed by a MIT license that can be found in the LICENSE file.
# SPDX-License-Identifier: MIT

from .v1.client import AnalyzeClient as AnalyzeClientLatest
from .v1.async_client import AsyncAnalyzeClient as AsyncAnalyzeClientLatest
from .v1.options import (
    # common
    AnalyzeOptions as AnalyzeOptionsLatest,
    UrlSource as UrlSourceLatest,
    TextSource as TextSourceLatest,
    BufferSource as BufferSourceLatest,
    StreamSource as StreamSourceLatest,
    FileSource as FileSourceLatest,
    # unique
    AnalyzeStreamSource as AnalyzeStreamSourceLatest,
    AnalyzeSource as AnalyzeSourceLatest,
)
from .v1.response import (
    SyncAnalyzeResponse as SyncAnalyzeResponseLatest,
    AnalyzeResponse as AnalyzeResponseLatest,
    AsyncAnalyzeResponse as AsyncAnalyzeResponseLatest,
    # shared
    Average as AverageLatest,
    Intent as IntentLatest,
    Intents as IntentsLatest,
    IntentsInfo as IntentsInfoLatest,
    Segment as SegmentLatest,
    SentimentInfo as SentimentInfoLatest,
    Sentiment as SentimentLatest,
    Sentiments as SentimentsLatest,
    SummaryInfo as SummaryInfoLatest,
    Topic as TopicLatest,
    Topics as TopicsLatest,
    TopicsInfo as TopicsInfoLatest,
    # unique
    Results as ResultsLatest,
    Metadata as MetadataLatest,
    Summary as SummaryLatest,
)

# The client.py points to the current supported version in the SDK.
# Older versions are supported in the SDK for backwards compatibility.

# common
UrlSource = UrlSourceLatest
TextSource = TextSourceLatest
BufferSource = BufferSourceLatest
StreamSource = StreamSourceLatest
FileSource = FileSourceLatest

AnalyzeStreamSource = AnalyzeStreamSourceLatest
AnalyzeSource = AnalyzeSourceLatest

# input
AnalyzeOptions = AnalyzeOptionsLatest

# responses
SyncAnalyzeResponse = SyncAnalyzeResponseLatest
AnalyzeResponse = AnalyzeResponseLatest
AsyncAnalyzeResponse = AsyncAnalyzeResponseLatest
# shared
Average = AverageLatest
Intent = IntentLatest
Intents = IntentsLatest
IntentsInfo = IntentsInfoLatest
Segment = SegmentLatest
SentimentInfo = SentimentInfoLatest
Sentiment = SentimentLatest
Sentiments = SentimentsLatest
SummaryInfo = SummaryInfoLatest
Topic = TopicLatest
Topics = TopicsLatest
TopicsInfo = TopicsInfoLatest
# unique
AnalyzeResults = ResultsLatest
AnalyzeMetadata = MetadataLatest
AnalyzeSummary = SummaryLatest

# clients
AnalyzeClient = AnalyzeClientLatest
AsyncAnalyzeClient = AsyncAnalyzeClientLatest


# aliases
ReadClient = AnalyzeClientLatest
AsyncReadClient = AsyncAnalyzeClientLatest


================================================
File: deepgram/clients/analyze/v1/__init__.py
================================================
# Copyright 2024 Deepgram SDK contributors. All Rights Reserved.
# Use of this source code is governed by a MIT license that can be found in the LICENSE file.
# SPDX-License-Identifier: MIT

from .client import AnalyzeClient
from .async_client import AsyncAnalyzeClient

# common
from .options import (
    UrlSource,
    TextSource,
    BufferSource,
    StreamSource,
    FileSource,
)

# analyze

from .options import (
    AnalyzeOptions,
    AnalyzeStreamSource,
    AnalyzeSource,
)

from .response import (
    AsyncAnalyzeResponse,
    SyncAnalyzeResponse,
    AnalyzeResponse,
    # shared
    Average,
    Intent,
    Intents,
    IntentsInfo,
    Segment,
    SentimentInfo,
    Sentiment,
    Sentiments,
    SummaryInfo,
    Topic,
    Topics,
    TopicsInfo,
    # unique
    Metadata,
    Results,
    Summary,
)


================================================
File: deepgram/clients/analyze/v1/async_client.py
================================================
# Copyright 2024 Deepgram SDK contributors. All Rights Reserved.
# Use of this source code is governed by a MIT license that can be found in the LICENSE file.
# SPDX-License-Identifier: MIT

import logging
from typing import Dict, Union, Optional

import httpx

from ....utils import verboselogs
from ....options import DeepgramClientOptions
from ...common import AbstractAsyncRestClient
from ...common import DeepgramError, DeepgramTypeError

from .helpers import is_buffer_source, is_readstream_source, is_url_source
from .options import (
    AnalyzeOptions,
    UrlSource,
    FileSource,
)
from .response import AsyncAnalyzeResponse, AnalyzeResponse


class AsyncAnalyzeClient(AbstractAsyncRestClient):
    """
    A client class for handling text data.
    Provides methods for transcribing text from URLs and files.
    """

    _logger: verboselogs.VerboseLogger
    _config: DeepgramClientOptions

    def __init__(self, config: DeepgramClientOptions):
        self._logger = verboselogs.VerboseLogger(__name__)
        self._logger.addHandler(logging.StreamHandler())
        self._logger.setLevel(config.verbose)
        self._config = config
        super().__init__(config)

    # pylint: disable=too-many-positional-arguments

    async def analyze_url(
        self,
        source: UrlSource,
        options: Optional[Union[AnalyzeOptions, Dict]] = None,
        addons: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        timeout: Optional[httpx.Timeout] = None,
        endpoint: str = "v1/read",
        **kwargs,
    ) -> Union[AsyncAnalyzeResponse, AnalyzeResponse]:
        """
        Analyze text from a URL source.

        Args:
            source (UrlSource): The URL source of the text to ingest.
            options (AnalyzeOptions): Additional options for the ingest (default is None).
            endpoint (str): The API endpoint for the ingest (default is "v1/read").

        Returns:
            AnalyzeResponse: An object containing the result.

        Raises:
            DeepgramTypeError: Raised for known API errors.
        """
        self._logger.debug("AsyncAnalyzeClient.analyze_url ENTER")

        if (
            isinstance(options, dict)
            and "callback" in options
            and options["callback"] is not None
        ) or (isinstance(options, AnalyzeOptions) and options.callback is not None):
            self._logger.debug("AsyncAnalyzeClient.analyze_url LEAVE")
            return await self.analyze_url_callback(
                source,
                callback=options["callback"],
                options=options,
                headers=headers,
                addons=addons,
                timeout=timeout,
                endpoint=endpoint,
                **kwargs,
            )

        url = f"{self._config.url}/{endpoint}"
        if is_url_source(source):
            body = source
        else:
            self._logger.error("Unknown transcription source type")
            self._logger.debug("AsyncAnalyzeClient.analyze_url LEAVE")
            raise DeepgramTypeError("Unknown transcription source type")

        if isinstance(options, AnalyzeOptions) and not options.check():
            self._logger.error("options.check failed")
            self._logger.debug("AsyncAnalyzeClient.analyze_url LEAVE")
            raise DeepgramError("Fatal transcription options error")

        self._logger.info("url: %s", url)
        self._logger.info("source: %s", source)
        if isinstance(options, AnalyzeOptions):
            self._logger.info("AnalyzeOptions switching class -> dict")
            options = options.to_dict()
        self._logger.info("options: %s", options)
        self._logger.info("addons: %s", addons)
        self._logger.info("headers: %s", headers)
        result = await self.post(
            url,
            options=options,
            addons=addons,
            headers=headers,
            json=body,
            timeout=timeout,
            **kwargs,
        )
        self._logger.info("json: %s", result)
        res = AnalyzeResponse.from_json(result)
        self._logger.verbose("result: %s", res)
        self._logger.notice("analyze_url succeeded")
        self._logger.debug("AsyncAnalyzeClient.analyze_url LEAVE")
        return res

    async def analyze_url_callback(
        self,
        source: UrlSource,
        callback: str,
        options: Optional[Union[AnalyzeOptions, Dict]] = None,
        addons: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        timeout: Optional[httpx.Timeout] = None,
        endpoint: str = "v1/read",
        **kwargs,
    ) -> AsyncAnalyzeResponse:
        """
        Transcribes audio from a URL source and sends the result to a callback URL.

        Args:
            source (UrlSource): The URL source of the audio to transcribe.
            callback (str): The callback URL where the transcription results will be sent.
            options (AnalyzeOptions): Additional options for the transcription (default is None).
            endpoint (str): The API endpoint for the transcription (default is "v1/read").

        Returns:
            AsyncAnalyzeResponse: An object containing the request_id or an error message.

        Raises:
            DeepgramTypeError: Raised for known API errors.
        """
        self._logger.debug("AnalyzeClient.analyze_url_callback ENTER")

        url = f"{self._config.url}/{endpoint}"
        if options is None:
            options = {}
        if isinstance(options, AnalyzeOptions):
            options.callback = callback
        else:
            options["callback"] = callback
        if is_url_source(source):
            body = source
        else:
            self._logger.error("Unknown transcription source type")
            self._logger.debug("AnalyzeClient.analyze_url_callback LEAVE")
            raise DeepgramTypeError("Unknown transcription source type")

        if isinstance(options, AnalyzeOptions) and not options.check():
            self._logger.error("options.check failed")
            self._logger.debug("AnalyzeClient.analyze_url_callback LEAVE")
            raise DeepgramError("Fatal transcription options error")

        self._logger.info("url: %s", url)
        self._logger.info("source: %s", source)
        if isinstance(options, AnalyzeOptions):
            self._logger.info("AnalyzeOptions switching class -> dict")
            options = options.to_dict()
        self._logger.info("options: %s", options)
        self._logger.info("addons: %s", addons)
        self._logger.info("headers: %s", headers)
        result = await self.post(
            url,
            options=options,
            addons=addons,
            headers=headers,
            json=body,
            timeout=timeout,
            **kwargs,
        )
        self._logger.info("json: %s", result)
        res = AsyncAnalyzeResponse.from_json(result)
        self._logger.verbose("result: %s", res)
        self._logger.notice("analyze_url_callback succeeded")
        self._logger.debug("AnalyzeClient.analyze_url_callback LEAVE")
        return res

    async def analyze_text(
        self,
        source: FileSource,
        options: Optional[Union[AnalyzeOptions, Dict]] = None,
        addons: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        timeout: Optional[httpx.Timeout] = None,
        endpoint: str = "v1/read",
        **kwargs,
    ) -> Union[AsyncAnalyzeResponse, AnalyzeResponse]:
        """
        Analyze text from a local file source.

        Args:
            source (TextSource): The local file source of the text to ingest.
            options (AnalyzeOptions): Additional options for the ingest (default is None).
            endpoint (str): The API endpoint for the transcription (default is "v1/read").

        Returns:
            AnalyzeResponse: An object containing the transcription result or an error message.

        Raises:
            DeepgramTypeError: Raised for known API errors.
        """
        self._logger.debug("AsyncAnalyzeClient.analyze_text ENTER")

        if (
            isinstance(options, dict)
            and "callback" in options
            and options["callback"] is not None
        ) or (isinstance(options, AnalyzeOptions) and options.callback is not None):
            self._logger.debug("AsyncAnalyzeClient.analyze_text LEAVE")
            return await self.analyze_text_callback(
                source,
                callback=options["callback"],
                options=options,
                headers=headers,
                addons=addons,
                timeout=timeout,
                endpoint=endpoint,
                **kwargs,
            )

        url = f"{self._config.url}/{endpoint}"
        if is_buffer_source(source):
            body = source["buffer"]  # type: ignore
        elif is_readstream_source(source):
            body = source["stream"]  # type: ignore
        else:
            self._logger.error("Unknown transcription source type")
            self._logger.debug("AsyncAnalyzeClient.analyze_text LEAVE")
            raise DeepgramTypeError("Unknown transcription source type")

        if isinstance(options, AnalyzeOptions) and not options.check():
            self._logger.error("options.check failed")
            self._logger.debug("AsyncAnalyzeClient.analyze_text LEAVE")
            raise DeepgramError("Fatal transcription options error")

        self._logger.info("url: %s", url)
        if isinstance(options, AnalyzeOptions):
            self._logger.info("AnalyzeOptions switching class -> dict")
            options = options.to_dict()
        self._logger.info("options: %s", options)
        self._logger.info("addons: %s", addons)
        self._logger.info("headers: %s", headers)
        result = await self.post(
            url,
            options=options,
            addons=addons,
            headers=headers,
            content=body,
            timeout=timeout,
            **kwargs,
        )
        self._logger.info("json: %s", result)
        res = AnalyzeResponse.from_json(result)
        self._logger.verbose("result: %s", res)
        self._logger.notice("analyze_text succeeded")
        self._logger.debug("AsyncAnalyzeClient.analyze_text LEAVE")
        return res

    async def analyze_text_callback(
        self,
        source: FileSource,
        callback: str,
        options: Optional[Union[AnalyzeOptions, Dict]] = None,
        addons: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        timeout: Optional[httpx.Timeout] = None,
        endpoint: str = "v1/read",
        **kwargs,
    ) -> AsyncAnalyzeResponse:
        """
        Transcribes audio from a local file source and sends the result to a callback URL.

        Args:
            source (TextSource): The local file source of the audio to transcribe.
            callback (str): The callback URL where the transcription results will be sent.
            options (AnalyzeOptions): Additional options for the transcription (default is None).
            endpoint (str): The API endpoint for the transcription (default is "v1/read").

        Returns:
            AsyncAnalyzeResponse: An object containing the request_id or an error message.

        Raises:
            DeepgramTypeError: Raised for known API errors.
        """
        self._logger.debug("AnalyzeClient.analyze_text_callback ENTER")

        url = f"{self._config.url}/{endpoint}"
        if options is None:
            options = {}
        if isinstance(options, AnalyzeOptions):
            options.callback = callback
        else:
            options["callback"] = callback
        if is_buffer_source(source):
            body = source["buffer"]  # type: ignore
        elif is_readstream_source(source):
            body = source["stream"]  # type: ignore
        else:
            self._logger.error("Unknown transcription source type")
            self._logger.debug("AnalyzeClient.analyze_text_callback LEAVE")
            raise DeepgramTypeError("Unknown transcription source type")

        if isinstance(options, AnalyzeOptions) and not options.check():
            self._logger.error("options.check failed")
            self._logger.debug("AnalyzeClient.analyze_text_callback LEAVE")
            raise DeepgramError("Fatal transcription options error")

        self._logger.info("url: %s", url)
        if isinstance(options, AnalyzeOptions):
            self._logger.info("AnalyzeOptions switching class -> dict")
            options = options.to_dict()
        self._logger.info("options: %s", options)
        self._logger.info("addons: %s", addons)
        self._logger.info("headers: %s", headers)
        result = await self.post(
            url,
            options=options,
            addons=addons,
            headers=headers,
            json=body,
            timeout=timeout,
            **kwargs,
        )
        self._logger.info("json: %s", result)
        res = AsyncAnalyzeResponse.from_json(result)
        self._logger.verbose("result: %s", res)
        self._logger.notice("analyze_text_callback succeeded")
        self._logger.debug("AnalyzeClient.analyze_text_callback LEAVE")
        return res

    # pylint: enable=too-many-positional-arguments


================================================
File: deepgram/clients/analyze/v1/client.py
================================================
# Copyright 2024 Deepgram SDK contributors. All Rights Reserved.
# Use of this source code is governed by a MIT license that can be found in the LICENSE file.
# SPDX-License-Identifier: MIT

import logging
from typing import Dict, Union, Optional

import httpx

from ....utils import verboselogs
from ....options import DeepgramClientOptions
from ...common import AbstractSyncRestClient
from ...common import DeepgramError, DeepgramTypeError

from .helpers import is_buffer_source, is_readstream_source, is_url_source
from .options import (
    AnalyzeOptions,
    UrlSource,
    FileSource,
)
from .response import AsyncAnalyzeResponse, AnalyzeResponse


class AnalyzeClient(AbstractSyncRestClient):
    """
    A client class for handling text data.
    Provides methods for transcribing text from URLs, files, etc.
    """

    _logger: verboselogs.VerboseLogger
    _config: DeepgramClientOptions

    def __init__(self, config: DeepgramClientOptions):
        self._logger = verboselogs.VerboseLogger(__name__)
        self._logger.addHandler(logging.StreamHandler())
        self._logger.setLevel(config.verbose)
        self._config = config
        super().__init__(config)

    # pylint: disable=too-many-positional-arguments

    def analyze_url(
        self,
        source: UrlSource,
        options: Optional[Union[AnalyzeOptions, Dict]] = None,
        addons: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        timeout: Optional[httpx.Timeout] = None,
        endpoint: str = "v1/read",
        **kwargs,
    ) -> Union[AnalyzeResponse, AsyncAnalyzeResponse]:
        """
        Analyze text from a URL source.

        Args:
            source (UrlSource): The URL source of the text to ingest.
            options (AnalyzeOptions): Additional options for the ingest (default is None).
            endpoint (str): The API endpoint for the ingest (default is "v1/read").

        Returns:
            AnalyzeResponse: An object containing the result.

        Raises:
            DeepgramTypeError: Raised for known API errors.
        """
        self._logger.debug("AnalyzeClient.analyze_url ENTER")

        if (
            isinstance(options, dict)
            and "callback" in options
            and options["callback"] is not None
        ) or (isinstance(options, AnalyzeOptions) and options.callback is not None):
            self._logger.debug("AnalyzeClient.analyze_url LEAVE")
            return self.analyze_url_callback(
                source,
                callback=options["callback"],
                options=options,
                addons=addons,
                headers=headers,
                timeout=timeout,
                endpoint=endpoint,
                **kwargs,
            )

        url = f"{self._config.url}/{endpoint}"
        if is_url_source(source):
            body = source
        else:
            self._logger.error("Unknown transcription source type")
            self._logger.debug("AnalyzeClient.analyze_url LEAVE")
            raise DeepgramTypeError("Unknown transcription source type")

        if isinstance(options, AnalyzeOptions) and not options.check():
            self._logger.error("options.check failed")
            self._logger.debug("AnalyzeClient.analyze_url LEAVE")
            raise DeepgramError("Fatal transcription options error")

        self._logger.info("url: %s", url)
        self._logger.info("source: %s", source)
        if isinstance(options, AnalyzeOptions):
            self._logger.info("AnalyzeOptions switching class -> dict")
            options = options.to_dict()
        self._logger.info("options: %s", options)
        self._logger.info("addons: %s", addons)
        self._logger.info("headers: %s", headers)
        result = self.post(
            url,
            options=options,
            addons=addons,
            headers=headers,
            json=body,
            timeout=timeout,
            **kwargs,
        )
        self._logger.info("json: %s", result)
        res = AnalyzeResponse.from_json(result)
        self._logger.verbose("result: %s", res)
        self._logger.notice("analyze_url succeeded")
        self._logger.debug("AnalyzeClient.analyze_url LEAVE")
        return res

    def analyze_url_callback(
        self,
        source: UrlSource,
        callback: str,
        options: Optional[Union[AnalyzeOptions, Dict]] = None,
        addons: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        timeout: Optional[httpx.Timeout] = None,
        endpoint: str = "v1/read",
        **kwargs,
    ) -> AsyncAnalyzeResponse:
        """
        Transcribes audio from a URL source and sends the result to a callback URL.

        Args:
            source (UrlSource): The URL source of the audio to transcribe.
            callback (str): The callback URL where the transcription results will be sent.
            options (AnalyzeOptions): Additional options for the transcription (default is None).
            endpoint (str): The API endpoint for the transcription (default is "v1/read").

        Returns:
            AsyncAnalyzeResponse: An object containing the request_id or an error message.

        Raises:
            DeepgramTypeError: Raised for known API errors.
        """
        self._logger.debug("AnalyzeClient.analyze_url_callback ENTER")

        url = f"{self._config.url}/{endpoint}"
        if options is None:
            options = {}
        if isinstance(options, AnalyzeOptions):
            options.callback = callback
        else:
            options["callback"] = callback
        if is_url_source(source):
            body = source
        else:
            self._logger.error("Unknown transcription source type")
            self._logger.debug("AnalyzeClient.analyze_url_callback LEAVE")
            raise DeepgramTypeError("Unknown transcription source type")

        if isinstance(options, AnalyzeOptions) and not options.check():
            self._logger.error("options.check failed")
            self._logger.debug("AnalyzeClient.analyze_url_callback LEAVE")
            raise DeepgramError("Fatal transcription options error")

        self._logger.info("url: %s", url)
        self._logger.info("source: %s", source)
        if isinstance(options, AnalyzeOptions):
            self._logger.info("AnalyzeOptions switching class -> dict")
            options = options.to_dict()
        self._logger.info("options: %s", options)
        self._logger.info("addons: %s", addons)
        self._logger.info("headers: %s", headers)
        result = self.post(
            url,
            options=options,
            addons=addons,
            headers=headers,
            json=body,
            timeout=timeout,
            **kwargs,
        )
        self._logger.info("json: %s", result)
        res = AsyncAnalyzeResponse.from_json(result)
        self._logger.verbose("result: %s", res)
        self._logger.notice("analyze_url_callback succeeded")
        self._logger.debug("AnalyzeClient.analyze_url_callback LEAVE")
        return res

    def analyze_text(
        self,
        source: FileSource,
        options: Optional[Union[AnalyzeOptions, Dict]] = None,
        addons: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        timeout: Optional[httpx.Timeout] = None,
        endpoint: str = "v1/read",
        **kwargs,
    ) -> Union[AnalyzeResponse, AsyncAnalyzeResponse]:
        """
        Analyze text from a local file source.

        Args:
            source (TextSource): The local file source of the text to ingest.
            options (AnalyzeOptions): Additional options for the ingest (default is None).
            endpoint (str): The API endpoint for the transcription (default is "v1/read").

        Returns:
            AnalyzeResponse: An object containing the transcription result or an error message.

        Raises:
            DeepgramTypeError: Raised for known API errors.
        """
        self._logger.debug("AnalyzeClient.analyze_text ENTER")

        if (
            isinstance(options, dict)
            and "callback" in options
            and options["callback"] is not None
        ) or (isinstance(options, AnalyzeOptions) and options.callback is not None):
            self._logger.debug("AnalyzeClient.analyze_text LEAVE")
            return self.analyze_text_callback(
                source,
                callback=options["callback"],
                options=options,
                addons=addons,
                headers=headers,
                timeout=timeout,
                endpoint=endpoint,
                **kwargs,
            )

        url = f"{self._config.url}/{endpoint}"
        if is_buffer_source(source):
            body = source["buffer"]  # type: ignore
        elif is_readstream_source(source):
            body = source["stream"]  # type: ignore
        else:
            self._logger.error("Unknown transcription source type")
            self._logger.debug("AnalyzeClient.analyze_text LEAVE")
            raise DeepgramTypeError("Unknown transcription source type")

        if isinstance(options, AnalyzeOptions) and not options.check():
            self._logger.error("options.check failed")
            self._logger.debug("AnalyzeClient.analyze_text LEAVE")
            raise DeepgramError("Fatal transcription options error")

        self._logger.info("url: %s", url)
        if isinstance(options, AnalyzeOptions):
            self._logger.info("AnalyzeOptions switching class -> dict")
            options = options.to_dict()
        self._logger.info("options: %s", options)
        self._logger.info("addons: %s", addons)
        self._logger.info("headers: %s", headers)
        result = self.post(
            url,
            options=options,
            addons=addons,
            headers=headers,
            content=body,
            timeout=timeout,
            **kwargs,
        )
        self._logger.info("json: %s", result)
        res = AnalyzeResponse.from_json(result)
        self._logger.verbose("result: %s", res)
        self._logger.notice("analyze_text succeeded")
        self._logger.debug("AnalyzeClient.analyze_text LEAVE")
        return res

    def analyze_text_callback(
        self,
        source: FileSource,
        callback: str,
        options: Optional[Union[AnalyzeOptions, Dict]] = None,
        addons: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        timeout: Optional[httpx.Timeout] = None,
        endpoint: str = "v1/read",
        **kwargs,
    ) -> AsyncAnalyzeResponse:
        """
        Transcribes audio from a local file source and sends the result to a callback URL.

        Args:
            source (TextSource): The local file source of the audio to transcribe.
            callback (str): The callback URL where the transcription results will be sent.
            options (AnalyzeOptions): Additional options for the transcription (default is None).
            endpoint (str): The API endpoint for the transcription (default is "v1/read").

        Returns:
            AsyncAnalyzeResponse: An object containing the request_id or an error message.

        Raises:
            DeepgramTypeError: Raised for known API errors.
        """
        self._logger.debug("AnalyzeClient.analyze_file_callback ENTER")

        url = f"{self._config.url}/{endpoint}"
        if options is None:
            options = {}
        if isinstance(options, AnalyzeOptions):
            options.callback = callback
        else:
            options["callback"] = callback
        if is_buffer_source(source):
            body = source["buffer"]  # type: ignore
        elif is_readstream_source(source):
            body = source["stream"]  # type: ignore
        else:
            self._logger.error("Unknown transcription source type")
            self._logger.debug("AnalyzeClient.analyze_file_callback LEAVE")
            raise DeepgramTypeError("Unknown transcription source type")

        if isinstance(options, AnalyzeOptions) and not options.check():
            self._logger.error("options.check failed")
            self._logger.debug("AnalyzeClient.analyze_file_callback LEAVE")
            raise DeepgramError("Fatal transcription options error")

        self._logger.info("url: %s", url)
        if isinstance(options, AnalyzeOptions):
            self._logger.info("AnalyzeOptions switching class -> dict")
            options = options.to_dict()
        self._logger.info("options: %s", options)
        self._logger.info("addons: %s", addons)
        self._logger.info("headers: %s", headers)
        result = self.post(
            url,
            options=options,
            addons=addons,
            headers=headers,
            json=body,
            timeout=timeout,
            **kwargs,
        )
        self._logger.info("json: %s", result)
        res = AsyncAnalyzeResponse.from_json(result)
        self._logger.verbose("result: %s", res)
        self._logger.notice("analyze_file_callback succeeded")
        self._logger.debug("AnalyzeClient.analyze_file_callback LEAVE")
        return res

    # pylint: enable=too-many-positional-arguments


================================================
File: deepgram/clients/analyze/v1/helpers.py
================================================
# Copyright 2023-2024 Deepgram SDK contributors. All Rights Reserved.
# Use of this source code is governed by a MIT license that can be found in the LICENSE file.
# SPDX-License-Identifier: MIT

from .options import AnalyzeSource


def is_buffer_source(provided_source: AnalyzeSource) -> bool:
    """
    Check if the provided source is a buffer source.
    """
    return "buffer" in provided_source


def is_readstream_source(provided_source: AnalyzeSource) -> bool:
    """
    Check if the provided source is a readstream source.
    """
    return "stream" in provided_source


def is_url_source(provided_source: AnalyzeSource) -> bool:
    """
    Check if the provided source is a url source.
    """
    return "url" in provided_source


================================================
File: deepgram/clients/analyze/v1/options.py
================================================
# Copyright 2024 Deepgram SDK contributors. All Rights Reserved.
# Use of this source code is governed by a MIT license that can be found in the LICENSE file.
# SPDX-License-Identifier: MIT

import logging
from typing import List, Union, Optional

from dataclasses import dataclass, field
from dataclasses_json import config as dataclass_config

from ....utils import verboselogs
from ...common import (
    TextSource,
    FileSource,
    BufferSource,
    StreamSource,
    UrlSource,
    BaseResponse,
)


@dataclass
class AnalyzeOptions(BaseResponse):  # pylint: disable=too-many-instance-attributes
    """
    Contains all the options for the AnalyzeOptions.

    Reference:
    https://developers.deepgram.com/reference/text-intelligence-apis
    """

    callback: Optional[str] = field(
        default=None, metadata=dataclass_config(exclude=lambda f: f is None)
    )
    callback_method: Optional[str] = field(
        default=None, metadata=dataclass_config(exclude=lambda f: f is None)
    )
    custom_intent: Optional[Union[List[str], str]] = field(
        default=None, metadata=dataclass_config(exclude=lambda f: f is None)
    )
    custom_intent_mode: Optional[str] = field(
        default=None, metadata=dataclass_config(exclude=lambda f: f is None)
    )
    custom_topic: Optional[Union[List[str], str]] = field(
        default=None, metadata=dataclass_config(exclude=lambda f: f is None)
    )
    custom_topic_mode: Optional[str] = field(
        default=None, metadata=dataclass_config(exclude=lambda f: f is None)
    )
    intents: Optional[bool] = field(
        default=None, metadata=dataclass_config(exclude=lambda f: f is None)
    )
    language: Optional[str] = field(
        default=None, metadata=dataclass_config(exclude=lambda f: f is None)
    )
    sentiment: Optional[bool] = field(
        default=None, metadata=dataclass_config(exclude=lambda f: f is None)
    )
    summarize: Optional[bool] = field(
        default=None, metadata=dataclass_config(exclude=lambda f: f is None)
    )
    topics: Optional[bool] = field(
        default=None, metadata=dataclass_config(exclude=lambda f: f is None)
    )

    def check(self):
        """
        Check the options for the AnalyzeOptions.
        """
        logger = verboselogs.VerboseLogger(__name__)
        logger.addHandler(logging.StreamHandler())
        prev = logger.level
        logger.setLevel(verboselogs.ERROR)

        # no op at the moment

        logger.setLevel(prev)

        return True


# unique
AnalyzeSource = Union[UrlSource, FileSource]
AnalyzeStreamSource = StreamSource


================================================
File: deepgram/clients/analyze/v1/response.py
================================================
# Copyright 2024 Deepgram SDK contributors. All Rights Reserved.
# Use of this source code is governed by a MIT license that can be found in the LICENSE file.
# SPDX-License-Identifier: MIT

from typing import List, Optional, Dict, Any

from dataclasses import dataclass, field
from dataclasses_json import config as dataclass_config

from ...common import (
    BaseResponse,
    Average,
    Intent,
    Intents,
    IntentsInfo,
    Segment,
    SentimentInfo,
    Sentiment,
    Sentiments,
    SummaryInfo,
    Topic,
    Topics,
    TopicsInfo,
)


# Async Analyze Response Types:


@dataclass
class AsyncAnalyzeResponse(BaseResponse):
    """
    Async Analyze Response
    """

    request_id: str = ""


# Analyze Response Types:


@dataclass
class Metadata(BaseResponse):
    """
    Metadata
    """

    request_id: str = ""
    created: str = ""
    language: str = ""
    intents_info: Optional[IntentsInfo] = field(
        default=None, metadata=dataclass_config(exclude=lambda f: f is None)
    )
    sentiment_info: Optional[SentimentInfo] = field(
        default=None, metadata=dataclass_config(exclude=lambda f: f is None)
    )
    summary_info: Optional[SummaryInfo] = field(
        default=None, metadata=dataclass_config(exclude=lambda f: f is None)
    )
    topics_info: Optional[TopicsInfo] = field(
        default=None, metadata=dataclass_config(exclude=lambda f: f is None)
    )

    def __getitem__(self, key):
        _dict = self.to_dict()
        if "intents_info" in _dict:
            _dict["intents_info"] = IntentsInfo.from_dict(_dict["intents_info"])
        if "sentiment_info" in _dict:
            _dict["sentiment_info"] = SentimentInfo.from_dict(_dict["sentiment_info"])
        if "summary_info" in _dict:
            _dict["summary_info"] = SummaryInfo.from_dict(_dict["summary_info"])
        if "topics_info" in _dict:
            _dict["topics_info"] = TopicsInfo.from_dict(_dict["topics_info"])
        return _dict[key]


@dataclass
class Summary(BaseResponse):
    """
    Summary
    """

    text: str = ""


@dataclass
class Results(BaseResponse):
    """
    Results
    """

    summary: Optional[Summary] = field(
        default=None, metadata=dataclass_config(exclude=lambda f: f is None)
    )
    sentiments: Optional[Sentiments] = field(
        default=None, metadata=dataclass_config(exclude=lambda f: f is None)
    )
    topics: Optional[Topics] = field(
        default=None, metadata=dataclass_config(exclude=lambda f: f is None)
    )
    intents: Optional[Intents] = field(
        default=None, metadata=dataclass_config(exclude=lambda f: f is None)
    )

    def __getitem__(self, key):
        _dict = self.to_dict()
        if "summary" in _dict:
            _dict["summary"] = Summary.from_dict(_dict["summary"])
        if "sentiments" in _dict:
            _dict["sentiments"] = Sentiments.from_dict(_dict["sentiments"])
        if "topics" in _dict:
            _dict["topics"] = Topics.from_dict(_dict["topics"])
        if "intents" in _dict:
            _dict["intents"] = Intents.from_dict(_dict["intents"])
        return _dict[key]


# Analyze Response Result:


@dataclass
class AnalyzeResponse(BaseResponse):
    """
    Analyze Response
    """

    metadata: Optional[Metadata] = field(
        default=None, metadata=dataclass_config(exclude=lambda f: f is None)
    )
    results: Optional[Results] = field(
        default=None, metadata=dataclass_config(exclude=lambda f: f is None)
    )

    def __getitem__(self, key):
        _dict = self.to_dict()
        if "metadata" in _dict:
            _dict["metadata"] = Metadata.from_dict(_dict["metadata"])
        if "results" in _dict:
            _dict["results"] = Results.from_dict(_dict["results"])
        return _dict[key]


SyncAnalyzeResponse = AnalyzeResponse


================================================
File: deepgram/clients/common/__init__.py
================================================
# Copyright 2023-2024 Deepgram SDK contributors. All Rights Reserved.
# Use of this source code is governed by a MIT license that can be found in the LICENSE file.
# SPDX-License-Identifier: MIT

from .v1 import (
    DeepgramError,
    DeepgramTypeError,
    DeepgramApiError,
    DeepgramUnknownApiError,
)

from .v1 import AbstractAsyncRestClient
from .v1 import AbstractSyncRestClient
from .v1 import AbstractAsyncWebSocketClient
from .v1 import AbstractSyncWebSocketClient

from .v1 import (
    TextSource as TextSourceLatest,
    BufferSource as BufferSourceLatest,
    StreamSource as StreamSourceLatest,
    FileSource as FileSourceLatest,
    UrlSource as UrlSourceLatest,
)

# shared
from .v1 import (
    BaseResponse as BaseResponseLatest,
    ModelInfo as ModelInfoLatest,
    Hit as HitLatest,
    Search as SearchLatest,
)

# rest
from .v1 import (
    Average as AverageLatest,
    Intent as IntentLatest,
    Intents as IntentsLatest,
    IntentsInfo as IntentsInfoLatest,
    Segment as SegmentLatest,
    SentimentInfo as SentimentInfoLatest,
    Sentiment as SentimentLatest,
    Sentiments as SentimentsLatest,
    SummaryInfo as SummaryInfoLatest,
    Topic as TopicLatest,
    Topics as TopicsLatest,
    TopicsInfo as TopicsInfoLatest,
)

# websocket
from .v1 import (
    OpenResponse as OpenResponseLatest,
    CloseResponse as CloseResponseLatest,
    ErrorResponse as ErrorResponseLatest,
    UnhandledResponse as UnhandledResponseLatest,
)

# export
UrlSource = UrlSourceLatest
TextSource = TextSourceLatest
BufferSource = BufferSourceLatest
StreamSource = StreamSourceLatest
FileSource = FileSourceLatest

BaseResponse = BaseResponseLatest
ModelInfo = ModelInfoLatest
Hit = HitLatest
Search = SearchLatest

Average = AverageLatest
Intent = IntentLatest
Intents = IntentsLatest
IntentsInfo = IntentsInfoLatest
Segment = SegmentLatest
SentimentInfo = SentimentInfoLatest
Sentiment = SentimentLatest
Sentiments = SentimentsLatest
SummaryInfo = SummaryInfoLatest
Topic = TopicLatest
Topics = TopicsLatest
TopicsInfo = TopicsInfoLatest

OpenResponse = OpenResponseLatest
CloseResponse = CloseResponseLatest
ErrorResponse = ErrorResponseLatest
UnhandledResponse = UnhandledResponseLatest


================================================
File: deepgram/clients/common/v1/__init__.py
================================================
# Copyright 2023-2024 Deepgram SDK contributors. All Rights Reserved.
# Use of this source code is governed by a MIT license that can be found in the LICENSE file.
# SPDX-License-Identifier: MIT

from .enums import Sentiment

from .errors import (
    DeepgramError,
    DeepgramTypeError,
    DeepgramApiError,
    DeepgramUnknownApiError,
)
from .abstract_async_rest import AbstractAsyncRestClient
from .abstract_sync_rest import AbstractSyncRestClient
from .abstract_async_websocket import AbstractAsyncWebSocketClient
from .abstract_sync_websocket import AbstractSyncWebSocketClient

from .options import (
    TextSource,
    BufferSource,
    StreamSource,
    FileSource,
    UrlSource,
)

from .shared_response import (
    BaseResponse,
    ModelInfo,
    Hit,
    Search,
)

from .rest_response import (
    Average,
    Intent,
    Intents,
    IntentsInfo,
    Segment,
    SentimentInfo,
    Sentiment,
    Sentiments,
    SummaryInfo,
    Topic,
    Topics,
    TopicsInfo,
)

from .websocket_response import (
    OpenResponse,
    CloseResponse,
    ErrorResponse,
    UnhandledResponse,
)


================================================
File: deepgram/clients/common/v1/abstract_async_rest.py
================================================
# Copyright 2023-2024 Deepgram SDK contributors. All Rights Reserved.
# Use of this source code is governed by a MIT license that can be found in the LICENSE file.
# SPDX-License-Identifier: MIT

import json
import io
from typing import Dict, Optional, List, Union

import httpx

from .helpers import append_query_params
from ....options import DeepgramClientOptions
from .errors import DeepgramError, DeepgramApiError, DeepgramUnknownApiError


class AbstractAsyncRestClient:
    """
    An abstract base class for a RESTful HTTP client.

    This class provides common HTTP methods (GET, POST, PUT, PATCH, DELETE) for making asynchronous HTTP requests.
    It handles error responses and provides basic JSON parsing.

    Args:
        url (Dict): The base URL for the RESTful API, including any path segments.
        headers (Optional[Dict[str, Any]]): Optional HTTP headers to include in requests.
        params (Optional[Dict[str, Any]]): Optional query parameters to include in requests.
        timeout (Optional[httpx.Timeout]): Optional timeout configuration for requests.

    Exceptions:
        DeepgramApiError: Raised for known API errors.
        DeepgramUnknownApiError: Raised for unknown API errors.
    """

    _config: DeepgramClientOptions

    def __init__(self, config: DeepgramClientOptions):
        if config is None:
            raise DeepgramError("Config are required")
        self._config = config

    # pylint: disable=too-many-positional-arguments

    async def get(
        self,
        url: str,
        options: Optional[Dict] = None,
        addons: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        timeout: Optional[httpx.Timeout] = None,
        **kwargs,
    ) -> str:
        """
        Make a GET request to the specified URL.
        """
        return await self._handle_request(
            "GET",
            url,
            params=options,
            addons=addons,
            headers=headers,
            timeout=timeout,
            **kwargs,
        )

    async def post_raw(
        self,
        url: str,
        options: Optional[Dict] = None,
        addons: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        timeout: Optional[httpx.Timeout] = None,
        **kwargs,
    ) -> httpx.Response:
        """
        Make a POST request to the specified URL and return response in raw bytes.
        """
        return await self._handle_request_raw(
            "POST",
            url,
            params=options,
            addons=addons,
            headers=headers,
            timeout=timeout,
            **kwargs,
        )

    async def post_memory(
        self,
        url: str,
        file_result: List,
        options: Optional[Dict] = None,
        addons: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        timeout: Optional[httpx.Timeout] = None,
        **kwargs,
    ) -> Dict[str, Union[str, io.BytesIO]]:
        """
        Make a POST request to the specified URL and return response in memory.
        """
        return await self._handle_request_memory(
            "POST",
            url,
            file_result=file_result,
            params=options,
            addons=addons,
            headers=headers,
            timeout=timeout,
            **kwargs,
        )

    async def post(
        self,
        url: str,
        options: Optional[Dict] = None,
        addons: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        timeout: Optional[httpx.Timeout] = None,
        **kwargs,
    ) -> str:
        """
        Make a POST request to the specified URL.
        """
        return await self._handle_request(
            "POST",
            url,
            params=options,
            addons=addons,
            headers=headers,
            timeout=timeout,
            **kwargs,
        )

    async def put(
        self,
        url: str,
        options: Optional[Dict] = None,
        addons: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        timeout: Optional[httpx.Timeout] = None,
        **kwargs,
    ) -> str:
        """
        Make a PUT request to the specified URL.
        """
        return await self._handle_request(
            "PUT",
            url,
            params=options,
            addons=addons,
            headers=headers,
            timeout=timeout,
            **kwargs,
        )

    async def patch(
        self,
        url: str,
        options: Optional[Dict] = None,
        addons: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        timeout: Optional[httpx.Timeout] = None,
        **kwargs,
    ) -> str:
        """
        Make a PATCH request to the specified URL.
        """
        return await self._handle_request(
            "PATCH",
            url,
            params=options,
            addons=addons,
            headers=headers,
            timeout=timeout,
            **kwargs,
        )

    async def delete(
        self,
        url: str,
        options: Optional[Dict] = None,
        addons: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        timeout: Optional[httpx.Timeout] = None,
        **kwargs,
    ) -> str:
        """
        Make a DELETE request to the specified URL.
        """
        return await self._handle_request(
            "DELETE",
            url,
            params=options,
            addons=addons,
            headers=headers,
            timeout=timeout,
            **kwargs,
        )

    # pylint: disable-msg=too-many-locals,too-many-branches,too-many-locals
    async def _handle_request(
        self,
        method: str,
        url: str,
        params: Optional[Dict] = None,
        addons: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        timeout: Optional[httpx.Timeout] = None,
        **kwargs,
    ) -> str:
        _url = url
        if params is not None:
            _url = append_query_params(_url, params)
        if addons is not None:
            _url = append_query_params(_url, addons)
        _headers = self._config.headers
        if headers is not None:
            _headers.update(headers)
        if timeout is None:
            timeout = httpx.Timeout(30.0, connect=10.0)

        try:
            transport = kwargs.get("transport")
            async with httpx.AsyncClient(
                timeout=timeout, transport=transport
            ) as client:
                if transport:
                    kwargs.pop("transport")
                response = await client.request(
                    method, _url, headers=_headers, **kwargs
                )
                response.raise_for_status()

                # throw exception if response is None or response.text is None
                if response is None or response.text is None:
                    raise DeepgramError(
                        "Response is not available yet. Please try again later."
                    )

                return response.text

        except httpx.HTTPError as e1:
            if isinstance(e1, httpx.HTTPStatusError):
                status_code = e1.response.status_code or 500
                try:
                    json_object = json.loads(e1.response.text)
                    raise DeepgramApiError(
                        json_object.get("err_msg"),
                        str(status_code),
                        json.dumps(json_object),
                    ) from e1
                except json.decoder.JSONDecodeError as e2:
                    raise DeepgramUnknownApiError(e2.msg, str(status_code)) from e2
                except ValueError as e2:
                    raise DeepgramUnknownApiError(str(e2), str(status_code)) from e2
            else:
                raise  # pylint: disable-msg=try-except-raise
        except Exception:  # pylint: disable-msg=try-except-raise
            raise

    # pylint: enable-msg=too-many-locals,too-many-branches,too-many-locals

    # pylint: disable-msg=too-many-locals,too-many-branches
    async def _handle_request_memory(
        self,
        method: str,
        url: str,
        file_result: List,
        params: Optional[Dict] = None,
        addons: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        timeout: Optional[httpx.Timeout] = None,
        **kwargs,
    ) -> Dict[str, Union[str, io.BytesIO]]:
        _url = url
        if params is not None:
            _url = append_query_params(_url, params)
        if addons is not None:
            _url = append_query_params(_url, addons)
        _headers = self._config.headers
        if headers is not None:
            _headers.update(headers)
        if timeout is None:
            timeout = httpx.Timeout(30.0, connect=10.0)

        try:
            transport = kwargs.get("transport")
            async with httpx.AsyncClient(
                timeout=timeout, transport=transport
            ) as client:
                if transport:
                    kwargs.pop("transport")
                response = await client.request(
                    method, _url, headers=_headers, **kwargs
                )
                response.raise_for_status()

                ret: Dict[str, Union[str, io.BytesIO]] = {}
                for item in file_result:
                    if item in response.headers:
                        ret[item] = response.headers[item]
                        continue
                    tmp_item = f"dg-{item}"
                    if tmp_item in response.headers:
                        ret[item] = response.headers[tmp_item]
                        continue
                    tmp_item = f"x-dg-{item}"
                    if tmp_item in response.headers:
                        ret[item] = response.headers[tmp_item]
                ret["stream"] = io.BytesIO(response.content)
                return ret

        except httpx.HTTPError as e1:
            if isinstance(e1, httpx.HTTPStatusError):
                status_code = e1.response.status_code or 500
                try:
                    json_object = json.loads(e1.response.text)
                    raise DeepgramApiError(
                        json_object.get("err_msg"),
                        str(status_code),
                        json.dumps(json_object),
                    ) from e1
                except json.decoder.JSONDecodeError as e2:
                    raise DeepgramUnknownApiError(e2.msg, str(status_code)) from e2
                except ValueError as e2:
                    raise DeepgramUnknownApiError(str(e2), str(status_code)) from e2
            else:
                raise  # pylint: disable-msg=try-except-raise
        except Exception:  # pylint: disable-msg=try-except-raise
            raise

    # pylint: enable-msg=too-many-locals,too-many-branches

    # pylint: disable-msg=too-many-locals,too-many-branches
    async def _handle_request_raw(
        self,
        method: str,
        url: str,
        params: Optional[Dict] = None,
        addons: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        timeout: Optional[httpx.Timeout] = None,
        **kwargs,
    ) -> httpx.Response:
        _url = url
        if params is not None:
            _url = append_query_params(_url, params)
        if addons is not None:
            _url = append_query_params(_url, addons)
        _headers = self._config.headers
        if headers is not None:
            _headers.update(headers)
        if timeout is None:
            timeout = httpx.Timeout(30.0, connect=10.0)

        try:
            transport = kwargs.get("transport")
            client = httpx.AsyncClient(timeout=timeout, transport=transport)
            if transport:
                kwargs.pop("transport")
            req = client.build_request(method, _url, headers=_headers, **kwargs)
            return await client.send(req, stream=True)

        except httpx.HTTPError as e1:
            if isinstance(e1, httpx.HTTPStatusError):
                status_code = e1.response.status_code or 500
                try:
                    json_object = json.loads(e1.response.text)
                    raise DeepgramApiError(
                        json_object.get("err_msg"),
                        str(status_code),
                        json.dumps(json_object),
                    ) from e1
                except json.decoder.JSONDecodeError as e2:
                    raise DeepgramUnknownApiError(e2.msg, str(status_code)) from e2
                except ValueError as e2:
                    raise DeepgramUnknownApiError(str(e2), str(status_code)) from e2
            else:
                raise  # pylint: disable-msg=try-except-raise
        except Exception:  # pylint: disable-msg=try-except-raise
            raise

    # pylint: enable-msg=too-many-locals,too-many-branches
    # pylint: enable=too-many-positional-arguments


================================================
File: deepgram/clients/common/v1/abstract_async_websocket.py
================================================
# Copyright 2023-2024 Deepgram SDK contributors. All Rights Reserved.
# Use of this source code is governed by a MIT license that can be found in the LICENSE file.
# SPDX-License-Identifier: MIT
import asyncio
import json
import logging
from typing import Dict, Union, Optional, cast, Any, Callable
from datetime import datetime
import threading
from abc import ABC, abstractmethod

import websockets

try:
    # Websockets versions >= 13
    from websockets.asyncio.client import connect, ClientConnection

    WS_ADDITIONAL_HEADERS_KEY = "additional_headers"
except ImportError:
    # Backward compatibility with websockets versions 12
    from websockets.legacy.client import (  # type: ignore
        connect,
        WebSocketClientProtocol as ClientConnection,
    )

    WS_ADDITIONAL_HEADERS_KEY = "extra_headers"

from ....audio import Speaker
from ....utils import verboselogs
from ....options import DeepgramClientOptions
from .helpers import convert_to_websocket_url, append_query_params
from .errors import DeepgramError

from .websocket_response import (
    OpenResponse,
    CloseResponse,
    ErrorResponse,
)
from .websocket_events import WebSocketEvents


ONE_SECOND = 1
HALF_SECOND = 0.5
DEEPGRAM_INTERVAL = 5
PING_INTERVAL = 20


class AbstractAsyncWebSocketClient(ABC):  # pylint: disable=too-many-instance-attributes
    """
    Abstract class for using WebSockets.

    This class provides methods to establish a WebSocket connection generically for
    use in all WebSocket clients.
    """

    _logger: verboselogs.VerboseLogger
    _config: DeepgramClientOptions
    _endpoint: str
    _websocket_url: str

    _socket: Optional[ClientConnection] = None

    _listen_thread: Union[asyncio.Task, None]
    _delegate: Optional[Speaker] = None

    _kwargs: Optional[Dict] = None
    _addons: Optional[Dict] = None
    _options: Optional[Dict] = None
    _headers: Optional[Dict] = None

    def __init__(self, config: DeepgramClientOptions, endpoint: str = ""):
        if config is None:
            raise DeepgramError("Config is required")
        if endpoint == "":
            raise DeepgramError("endpoint is required")

        self._logger = verboselogs.VerboseLogger(__name__)
        self._logger.addHandler(logging.StreamHandler())
        self._logger.setLevel(config.verbose)

        self._config = config
        self._endpoint = endpoint

        self._listen_thread = None

        # events
        self._exit_event = asyncio.Event()

        # set websocket url
        self._websocket_url = convert_to_websocket_url(self._config.url, self._endpoint)

    def delegate_listening(self, delegate: Speaker) -> None:
        """
        Delegate the listening thread to the Speaker object.
        """
        self._delegate = delegate

    # pylint: disable=too-many-branches,too-many-statements
    async def start(
        self,
        options: Optional[Any] = None,
        addons: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        **kwargs,
    ) -> bool:
        """
        Starts the WebSocket connection for live transcription.
        """
        self._logger.debug("AbstractAsyncWebSocketClient.start ENTER")
        self._logger.info("addons: %s", addons)
        self._logger.info("headers: %s", headers)
        self._logger.info("kwargs: %s", kwargs)

        self._addons = addons
        self._headers = headers

        # set kwargs
        if kwargs is not None:
            self._kwargs = kwargs
        else:
            self._kwargs = {}

        if not isinstance(options, dict):
            self._logger.error("options is not a dict")
            self._logger.debug("AbstractSyncWebSocketClient.start LEAVE")
            return False

        # set options
        if options is not None:
            self._options = options
        else:
            self._options = {}

        combined_options = self._options.copy()
        if self._addons is not None:
            self._logger.info("merging addons to options")
            combined_options.update(self._addons)
            self._logger.info("new options: %s", combined_options)
        self._logger.debug("combined_options: %s", combined_options)

        combined_headers = self._config.headers.copy()
        if self._headers is not None:
            self._logger.info("merging headers to options")
            combined_headers.update(self._headers)
            self._logger.info("new headers: %s", combined_headers)
        self._logger.debug("combined_headers: %s", combined_headers)

        url_with_params = append_query_params(self._websocket_url, combined_options)

        try:
            ws_connect_kwargs: Dict = {
                "ping_interval": PING_INTERVAL,
                WS_ADDITIONAL_HEADERS_KEY: combined_headers,
            }

            self._socket = await connect(
                url_with_params,
                **ws_connect_kwargs,
            )
            self._exit_event.clear()

            # debug the threads
            for thread in threading.enumerate():
                self._logger.debug("after running thread: %s", thread.name)
            self._logger.debug("number of active threads: %s", threading.active_count())

            # delegate the listening thread to external object
            if self._delegate is not None:
                self._logger.notice("_delegate is enabled. this is usually the speaker")
                self._delegate.set_pull_callback(self._socket.recv)
                self._delegate.set_push_callback(self._process_message)
            else:
                self._logger.notice("create _listening thread")
                self._listen_thread = asyncio.create_task(self._listening())

            # debug the threads
            for thread in threading.enumerate():
                self._logger.debug("after running thread: %s", thread.name)
            self._logger.debug("number of active threads: %s", threading.active_count())

            # push open event
            await self._emit(
                WebSocketEvents(WebSocketEvents.Open),
                OpenResponse(type=WebSocketEvents.Open),
            )

            self._logger.notice("start succeeded")
            self._logger.debug("AbstractAsyncWebSocketClient.start LEAVE")
            return True
        except websockets.exceptions.ConnectionClosed as e:
            self._logger.error(
                "ConnectionClosed in AbstractAsyncWebSocketClient.start: %s", e
            )
            self._logger.debug("AbstractAsyncWebSocketClient.start LEAVE")
            if self._config.options.get("termination_exception_connect", False):
                raise
            return False
        except websockets.exceptions.WebSocketException as e:
            self._logger.error(
                "WebSocketException in AbstractAsyncWebSocketClient.start: %s", e
            )
            self._logger.debug("AbstractAsyncWebSocketClient.start LEAVE")
            if self._config.options.get("termination_exception_connect", False):
                raise
            return False
        except Exception as e:  # pylint: disable=broad-except
            self._logger.error(
                "WebSocketException in AbstractAsyncWebSocketClient.start: %s", e
            )
            self._logger.debug("AbstractAsyncWebSocketClient.start LEAVE")
            if self._config.options.get("termination_exception_connect", False):
                raise
            return False

    async def is_connected(self) -> bool:
        """
        Returns the connection status of the WebSocket.
        """
        return self._socket is not None

    # pylint: enable=too-many-branches,too-many-statements

    @abstractmethod
    def on(self, event: WebSocketEvents, handler: Callable) -> None:
        """
        Registers an event handler for the WebSocket connection.
        """
        raise NotImplementedError("no on method")

    @abstractmethod
    async def _emit(self, event: WebSocketEvents, *args, **kwargs) -> None:
        """
        Emits an event to the WebSocket connection.
        """
        raise NotImplementedError("no _emit method")

    # pylint: disable=too-many-return-statements,too-many-statements,too-many-locals,too-many-branches
    async def _listening(self) -> None:
        """
        Listens for messages from the WebSocket connection.
        """
        self._logger.debug("AbstractAsyncWebSocketClient._listening ENTER")

        while True:
            try:
                if self._exit_event.is_set():
                    self._logger.notice("_listening exiting gracefully")
                    self._logger.debug("AbstractAsyncWebSocketClient._listening LEAVE")
                    return

                if self._socket is None:
                    self._logger.warning("socket is empty")
                    self._logger.debug("AbstractAsyncWebSocketClient._listening LEAVE")
                    return

                message = await self._socket.recv()

                if message is None:
                    self._logger.info("message is None")
                    continue

                self._logger.spam("data type: %s", type(message))

                if isinstance(message, bytes):
                    self._logger.debug("Binary data received")
                    await self._process_binary(message)
                else:
                    self._logger.debug("Text data received")
                    await self._process_text(message)

                self._logger.notice("_listening Succeeded")
                self._logger.debug("AbstractAsyncWebSocketClient._listening LEAVE")

            except websockets.exceptions.ConnectionClosedOK as e:
                # signal exit and close
                await self._signal_exit()

                self._logger.notice(f"_listening({e.code}) exiting gracefully")
                self._logger.debug("AbstractAsyncWebSocketClient._listening LEAVE")
                return

            except websockets.exceptions.ConnectionClosed as e:
                if e.code in [1000, 1001]:
                    # signal exit and close
                    await self._signal_exit()

                    self._logger.notice(f"_listening({e.code}) exiting gracefully")
                    self._logger.debug("AbstractAsyncWebSocketClient._listening LEAVE")
                    return

                # we need to explicitly call self._signal_exit() here because we are hanging on a recv()
                # note: this is different than the speak websocket client
                self._logger.error(
                    "ConnectionClosed in AbstractAsyncWebSocketClient._listening with code %s: %s",
                    e.code,
                    e.reason,
                )
                cc_error: ErrorResponse = ErrorResponse(
                    "ConnectionClosed in AbstractAsyncWebSocketClient._listening",
                    f"{e}",
                    "ConnectionClosed",
                )
                await self._emit(
                    WebSocketEvents(WebSocketEvents.Error),
                    error=cc_error,
                    **dict(cast(Dict[Any, Any], self._kwargs)),
                )

                # signal exit and close
                await self._signal_exit()

                self._logger.debug("AbstractAsyncWebSocketClient._listening LEAVE")

                if self._config.options.get("termination_exception_connect") is True:
                    raise
                return

            except websockets.exceptions.WebSocketException as e:
                self._logger.error(
                    "WebSocketException in AbstractAsyncWebSocketClient._listening: %s",
                    e,
                )
                ws_error: ErrorResponse = ErrorResponse(
                    "WebSocketException in AbstractAsyncWebSocketClient._listening",
                    f"{e}",
                    "WebSocketException",
                )
                await self._emit(
                    WebSocketEvents(WebSocketEvents.Error),
                    error=ws_error,
                    **dict(cast(Dict[Any, Any], self._kwargs)),
                )

                # signal exit and close
                await self._signal_exit()

                self._logger.debug("AbstractAsyncWebSocketClient._listening LEAVE")

                if self._config.options.get("termination_exception_connect") is True:
                    raise
                return

            except Exception as e:  # pylint: disable=broad-except
                self._logger.error(
                    "Exception in AbstractAsyncWebSocketClient._listening: %s", e
                )
                e_error: ErrorResponse = ErrorResponse(
                    "Exception in AbstractAsyncWebSocketClient._listening",
                    f"{e}",
                    "Exception",
                )
                await self._emit(
                    WebSocketEvents(WebSocketEvents.Error),
                    error=e_error,
                    **dict(cast(Dict[Any, Any], self._kwargs)),
                )

                # signal exit and close
                await self._signal_exit()

                self._logger.debug("AbstractAsyncWebSocketClient._listening LEAVE")

                if self._config.options.get("termination_exception_connect") is True:
                    raise
                return

    # pylint: enable=too-many-return-statements,too-many-statements,too-many-locals,too-many-branches

    async def _process_message(self, message: Union[str, bytes]) -> None:
        if isinstance(message, bytes):
            await self._process_binary(message)
        else:
            await self._process_text(message)

    @abstractmethod
    async def _process_text(self, message: str) -> None:
        raise NotImplementedError("no _process_text method")

    @abstractmethod
    async def _process_binary(self, message: bytes) -> None:
        raise NotImplementedError("no _process_binary method")

    @abstractmethod
    async def _close_message(self) -> bool:
        raise NotImplementedError("no _close_message method")

    # pylint: disable=too-many-return-statements,too-many-branches

    async def send(self, data: Union[str, bytes]) -> bool:
        """
        Sends data over the WebSocket connection.
        """
        self._logger.spam("AbstractAsyncWebSocketClient.send ENTER")

        if self._exit_event.is_set():
            self._logger.notice("send exiting gracefully")
            self._logger.debug("AbstractAsyncWebSocketClient.send LEAVE")
            return False

        if not await self.is_connected():
            self._logger.notice("is_connected is False")
            self._logger.debug("AbstractAsyncWebSocketClient.send LEAVE")
            return False

        if self._socket is not None:
            try:
                await self._socket.send(data)
            except websockets.exceptions.ConnectionClosedOK as e:
                self._logger.notice(f"send() exiting gracefully: {e.code}")
                self._logger.debug("AbstractAsyncWebSocketClient.send LEAVE")
                if self._config.options.get("termination_exception_send") is True:
                    raise
                return True
            except websockets.exceptions.ConnectionClosed as e:
                if e.code in [1000, 1001]:
                    self._logger.notice(f"send({e.code}) exiting gracefully")
                    self._logger.debug("AbstractAsyncWebSocketClient.send LEAVE")
                    if self._config.options.get("termination_exception_send") is True:
                        raise
                    return True

                self._logger.error("send() failed - ConnectionClosed: %s", str(e))
                self._logger.spam("AbstractAsyncWebSocketClient.send LEAVE")
                if self._config.options.get("termination_exception_send") is True:
                    raise
                return False
            except websockets.exceptions.WebSocketException as e:
                self._logger.error("send() failed - WebSocketException: %s", str(e))
                self._logger.spam("AbstractAsyncWebSocketClient.send LEAVE")
                if self._config.options.get("termination_exception_send") is True:
                    raise
                return False
            except Exception as e:  # pylint: disable=broad-except
                self._logger.error("send() failed - Exception: %s", str(e))
                self._logger.spam("AbstractAsyncWebSocketClient.send LEAVE")
                if self._config.options.get("termination_exception_send") is True:
                    raise
                return False

            self._logger.spam("send() succeeded")
            self._logger.spam("AbstractAsyncWebSocketClient.send LEAVE")
            return True

        self._logger.spam("send() failed. socket is None")
        self._logger.spam("AbstractAsyncWebSocketClient.send LEAVE")
        return False

    # pylint: enable=too-many-return-statements,too-many-branches

    async def finish(self) -> bool:
        """
        Closes the WebSocket connection gracefully.
        """
        self._logger.debug("AbstractAsyncWebSocketClient.finish ENTER")

        # signal exit
        await self._signal_exit()

        # stop the threads
        self._logger.verbose("cancelling tasks...")
        try:
            # Before cancelling, check if the tasks were created
            # debug the threads
            for thread in threading.enumerate():
                self._logger.debug("before running thread: %s", thread.name)
            self._logger.debug("number of active threads: %s", threading.active_count())

            tasks = []
            if self._listen_thread is not None:
                self._listen_thread.cancel()
                tasks.append(self._listen_thread)
                self._logger.notice("processing _listen_thread cancel...")

            # Use asyncio.gather to wait for tasks to be cancelled
            await asyncio.gather(*filter(None, tasks))
            self._logger.notice("threads joined")

            # debug the threads
            for thread in threading.enumerate():
                if thread is not None and thread.name is not None:
                    self._logger.debug("after running thread: %s", thread.name)
                else:
                    self._logger.debug("after running thread: unknown_thread_name")
            self._logger.debug("number of active threads: %s", threading.active_count())

            self._logger.notice("finish succeeded")
            self._logger.spam("AbstractAsyncWebSocketClient.finish LEAVE")
            return True

        except asyncio.CancelledError as e:
            self._logger.error("tasks cancelled error: %s", e)
            self._logger.debug("AbstractAsyncWebSocketClient.finish LEAVE")
            return True

    async def _signal_exit(self) -> None:
        # send close event
        self._logger.verbose("closing socket...")
        if self._socket is not None:
            self._logger.verbose("send Close...")
            try:
                # if the socket connection is closed, the following line might throw an error
                await self._close_message()
            except websockets.exceptions.ConnectionClosedOK as e:
                self._logger.notice("_signal_exit  - ConnectionClosedOK: %s", e.code)
            except websockets.exceptions.ConnectionClosed as e:
                self._logger.error("_signal_exit  - ConnectionClosed: %s", e.code)
            except websockets.exceptions.WebSocketException as e:
                self._logger.error("_signal_exit - WebSocketException: %s", str(e))
            except Exception as e:  # pylint: disable=broad-except
                self._logger.error("_signal_exit - Exception: %s", str(e))

            # push close event
            try:
                await self._emit(
                    WebSocketEvents(WebSocketEvents.Close),
                    close=CloseResponse(type=WebSocketEvents.Close),
                    **dict(cast(Dict[Any, Any], self._kwargs)),
                )
            except Exception as e:  # pylint: disable=broad-except
                self._logger.error("_emit - Exception: %s", e)

            # wait for task to send
            await asyncio.sleep(0.5)

        # signal exit
        self._exit_event.set()

        # closes the WebSocket connection gracefully
        self._logger.verbose("clean up socket...")
        if self._socket is not None:
            self._logger.verbose("socket.wait_closed...")
            try:
                await self._socket.close()
            except websockets.exceptions.WebSocketException as e:
                self._logger.error("socket.wait_closed failed: %s", e)

        self._socket = None


================================================
File: deepgram/clients/common/v1/abstract_sync_rest.py
================================================
# Copyright 2023-2024 Deepgram SDK contributors. All Rights Reserved.
# Use of this source code is governed by a MIT license that can be found in the LICENSE file.
# SPDX-License-Identifier: MIT

import json
import io
from typing import Dict, Optional, List, Union

import httpx

from .helpers import append_query_params
from ....options import DeepgramClientOptions
from .errors import DeepgramError, DeepgramApiError, DeepgramUnknownApiError


class AbstractSyncRestClient:
    """
    An abstract base class for a RESTful HTTP client.

    This class provides common HTTP methods (GET, POST, PUT, PATCH, DELETE) for making asynchronous HTTP requests.
    It handles error responses and provides basic JSON parsing.

    Args:
        url (Dict): The base URL for the RESTful API, including any path segments.
        headers (Optional[Dict[str, Any]]): Optional HTTP headers to include in requests.
        params (Optional[Dict[str, Any]]): Optional query parameters to include in requests.
        timeout (Optional[httpx.Timeout]): Optional timeout configuration for requests.

    Exceptions:
        DeepgramApiError: Raised for known API errors.
        DeepgramUnknownApiError: Raised for unknown API errors.
    """

    _config: DeepgramClientOptions

    def __init__(self, config: DeepgramClientOptions):
        if config is None:
            raise DeepgramError("Config are required")
        self._config = config

    # pylint: disable=too-many-positional-arguments

    def get(
        self,
        url: str,
        options: Optional[Dict] = None,
        addons: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        timeout: Optional[httpx.Timeout] = None,
        **kwargs,
    ) -> str:
        """
        Make a GET request to the specified URL.
        """
        return self._handle_request(
            "GET",
            url,
            params=options,
            addons=addons,
            headers=headers,
            timeout=timeout,
            **kwargs,
        )

    d