import os

import pytest
from click.testing import CliRunner  # type: ignore
from librelingo_fakes import fakes
from librelingo_json_export.cli import DEFAULT_SETTINGS, main


@pytest.fixture
def inputs():
    return str(fakes.fake_value()), str(fakes.fake_value())


@pytest.fixture
def mocks(mocker):
    load_course = mocker.patch("librelingo_json_export.cli.load_course")
    load_course.return_value = fakes.fake_value()
    return {
        "load_course": load_course,
        "export_course": mocker.patch("librelingo_json_export.cli.export_course"),
    }


@pytest.fixture
def invoke(mocks, fs):
    def f(args):
        runner = CliRunner()
        return runner.invoke(main, args)

    return f


def test_yaml_to_json_loads_correct_course(mocks, inputs, invoke):
    invoke(inputs)
    mocks["load_course"].assert_called_with(inputs[0])


def test_yaml_to_json_exports_correct_course(mocks, inputs, invoke):
    invoke(inputs)
    mocks["export_course"].assert_called_with(
        inputs[1], mocks["load_course"].return_value, DEFAULT_SETTINGS
    )


def test_yaml_to_json_has_help_text(mocks, inputs, invoke):
    assert main.help


def test_creates_output_directory_if_it_doesnt_exist(mocks, inputs, invoke, fs):
    output_path = "foo/500/bar"
    invoke([inputs[0], output_path])
    assert os.path.isdir(output_path)


def test_has_a_dry_run_option(mocks, inputs, invoke):
    result = invoke([*inputs, "--dry-run"])
    assert result.exit_code == 0


def test_dry_run_doesnt_create_output_files(inputs, invoke):
    files_before_dry_run = tuple(os.walk("."))
    invoke([*inputs, "--dry-run"])
    assert tuple(os.walk(".")) == files_before_dry_run


def test_dry_run_calls_real_export_course(mocks, inputs, invoke):
    invoke([*inputs, "--dry-run"])
    assert mocks["export_course"].call_count == 1
