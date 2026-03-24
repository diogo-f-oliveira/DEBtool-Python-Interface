from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover
    import tomli as tomllib


EXPECTED_TIER_FILES = (
    "pars.csv",
    "entity_data_errors.csv",
    "group_data_errors.csv",
    "result_metadata.json",
    "result_summary.json",
)


class ReleaseValidationError(RuntimeError):
    """Raised when release validation cannot complete successfully."""


@dataclass
class ExampleDescriptor:
    name: str
    path: Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build, install, and validate the release artifact against all examples.",
    )
    parser.add_argument(
        "--env-name",
        default="debtoolpyif_test",
        help="Conda environment used for uninstall/install and example execution.",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=None,
        help="Optional root folder for temporary validation outputs.",
    )
    parser.add_argument(
        "--keep-artifacts",
        action="store_true",
        help="Keep temporary validation outputs even when the run succeeds.",
    )
    parser.add_argument(
        "--estimation-settings",
        choices=("fast", "end-to-end"),
        default="fast",
        help="Select which example estimation settings to use during validation.",
    )
    return parser.parse_args()


def load_project_metadata(repo_root: Path) -> tuple[str, str]:
    pyproject_path = repo_root / "pyproject.toml"
    with pyproject_path.open("rb") as handle:
        pyproject = tomllib.load(handle)
    project = pyproject["project"]
    return project["name"], project["version"]


def discover_examples(repo_root: Path) -> list[ExampleDescriptor]:
    examples_root = repo_root / "examples"
    discovered = []
    for folder in sorted(examples_root.iterdir()):
        if (
            folder.is_dir()
            and (folder / "data.py").is_file()
            and (folder / "tier_structure.py").is_file()
            and (folder / "estimation.py").is_file()
            and (folder / "data").is_dir()
        ):
            discovered.append(ExampleDescriptor(name=folder.name, path=folder))
    if not discovered:
        raise ReleaseValidationError(f"No examples discovered under {examples_root}.")
    return discovered


def print_section(title: str) -> None:
    print(f"\n== {title} ==")


def run_command(
    args: list[str],
    *,
    cwd: Path,
    env: dict[str, str] | None = None,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        args,
        cwd=str(cwd),
        env=env,
        check=False,
        text=True,
        capture_output=True,
    )
    if result.stdout:
        print(result.stdout, end="" if result.stdout.endswith("\n") else "\n")
    if result.stderr:
        print(result.stderr, end="" if result.stderr.endswith("\n") else "\n", file=sys.stderr)
    if check and result.returncode != 0:
        raise ReleaseValidationError(
            f"Command failed with exit code {result.returncode}: {' '.join(args)}"
        )
    return result


def locate_built_wheel(dist_dir: Path, package_name: str, version: str) -> Path:
    normalized = package_name.replace("-", "_")
    candidates = [
        path for path in dist_dir.glob("*.whl")
        if version in path.name and normalized.lower() in path.name.lower()
    ]
    if not candidates:
        raise ReleaseValidationError(
            f"Could not find a built wheel for {package_name} {version} in {dist_dir}."
        )
    candidates.sort(key=lambda path: path.stat().st_mtime, reverse=True)
    return candidates[0]


def build_wheel(repo_root: Path, package_name: str, version: str) -> Path:
    print_section("Build")
    print(f"Building {package_name} {version}")
    run_command([sys.executable, "-m", "build", "--wheel", "--no-isolation"], cwd=repo_root)
    wheel_path = locate_built_wheel(repo_root / "dist", package_name, version)
    print(f"Built wheel: {wheel_path}")
    return wheel_path


def conda_python_command(env_name: str) -> list[str]:
    conda_exe = os.environ.get("CONDA_EXE") or shutil.which("conda")
    if not conda_exe:
        raise ReleaseValidationError(
            "Could not locate the conda executable. Run the script from a conda-enabled shell or environment."
        )
    return [conda_exe, "run", "-n", env_name, "python"]


def uninstall_previous_version(repo_root: Path, env_name: str, package_name: str) -> None:
    print_section("Uninstall Previous Version")
    result = run_command(
        conda_python_command(env_name) + ["-m", "pip", "uninstall", "-y", package_name],
        cwd=repo_root,
        check=False,
    )
    if result.returncode == 0:
        print(f"Previous {package_name} installation removed from {env_name}.")
        return

    combined_output = f"{result.stdout}\n{result.stderr}"
    not_installed_markers = (
        f"Skipping {package_name} as it is not installed",
        f"WARNING: Skipping {package_name} as it is not installed",
        f"WARNING: Skipping {package_name.lower()} as it is not installed",
    )
    if any(marker in combined_output for marker in not_installed_markers):
        print(f"No previous {package_name} installation found in {env_name}.")
        return

    raise ReleaseValidationError(f"Unable to uninstall previous {package_name} from {env_name}.")


def install_wheel(repo_root: Path, env_name: str, wheel_path: Path) -> None:
    print_section("Install New Version")
    run_command(
        conda_python_command(env_name) + ["-m", "pip", "install", "--force-reinstall", "--no-deps", str(wheel_path)],
        cwd=repo_root,
    )
    print(f"Installed wheel into {env_name}: {wheel_path.name}")


def confirm_installed_version(repo_root: Path, env_name: str, package_name: str, version: str) -> None:
    print_section("Confirm Installed Package")
    script = (
        "import importlib.metadata as m; "
        f"print(m.version('{package_name}'))"
    )
    result = run_command(
        conda_python_command(env_name) + ["-c", script],
        cwd=repo_root,
    )
    installed_version = result.stdout.strip().splitlines()[-1]
    if installed_version != version:
        raise ReleaseValidationError(
            f"Installed version mismatch in {env_name}: expected {version}, got {installed_version}."
        )
    print(f"Installed version confirmed: {installed_version}")


def create_staging_root(repo_root: Path, output_root: Path | None) -> Path:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    if output_root is None:
        output_root = repo_root / "tmp" / "release_validate"
    staging_root = output_root / timestamp
    staging_root.mkdir(parents=True, exist_ok=True)
    return staging_root


def write_runner_script(staging_root: Path) -> Path:
    runner_path = staging_root / "run_installed_examples.py"
    runner_path.write_text(
        """
from __future__ import annotations

import importlib
import json
import os
import sys
from pathlib import Path

import pandas as pd

EXPECTED_TIER_FILES = (
    "pars.csv",
    "entity_data_errors.csv",
    "group_data_errors.csv",
    "result_metadata.json",
    "result_summary.json",
)


def fail(message: str) -> None:
    raise RuntimeError(message)


def discover_examples(examples_root: Path) -> list[Path]:
    examples = []
    for folder in sorted(examples_root.iterdir()):
        if (
            folder.is_dir()
            and (folder / "data.py").is_file()
            and (folder / "tier_structure.py").is_file()
            and (folder / "estimation.py").is_file()
            and (folder / "data").is_dir()
        ):
            examples.append(folder)
    return examples


def assert_non_empty_csv(csv_path: Path) -> None:
    if not csv_path.is_file():
        fail(f"Missing expected CSV: {csv_path}")
    frame = pd.read_csv(csv_path)
    if frame.empty:
        fail(f"CSV is empty: {csv_path}")


def verify_installed_package(repo_root: Path) -> str:
    import DEBtoolPyIF

    package_path = Path(DEBtoolPyIF.__file__).resolve()
    src_root = (repo_root / "src").resolve()
    if src_root in package_path.parents:
        fail(f"Package resolved from source tree instead of installed environment: {package_path}")
    if repo_root.resolve() in package_path.parents and "site-packages" not in str(package_path):
        fail(f"Package resolved from repo tree instead of installed environment: {package_path}")
    return str(package_path)


def verify_outputs(multitier, output_folder: Path) -> list[dict]:
    if not output_folder.is_dir():
        fail(f"Output folder was not created: {output_folder}")
    entity_vs_tier = output_folder / "entity_vs_tier.csv"
    if not entity_vs_tier.is_file():
        fail(f"Root multitier file missing: {entity_vs_tier}")

    summaries = []
    for tier_name in multitier.tier_names:
        tier = multitier.tiers[tier_name]
        tier_output_folder = Path(tier.output_folder)
        if not tier_output_folder.is_dir():
            fail(f"Tier output folder missing for {tier_name}: {tier_output_folder}")
        if not getattr(tier, "estimation_complete", False):
            fail(f"Tier estimation did not complete for {tier_name}")

        for filename in EXPECTED_TIER_FILES:
            file_path = tier_output_folder / filename
            if not file_path.is_file():
                fail(f"Expected tier output file missing for {tier_name}: {file_path}")

        assert_non_empty_csv(tier_output_folder / "pars.csv")
        assert_non_empty_csv(tier_output_folder / "entity_data_errors.csv")
        assert_non_empty_csv(tier_output_folder / "group_data_errors.csv")

        metadata = json.loads((tier_output_folder / "result_metadata.json").read_text(encoding="utf-8"))
        summary = json.loads((tier_output_folder / "result_summary.json").read_text(encoding="utf-8"))
        if metadata.get("tier_name") != tier_name:
            fail(f"Metadata tier_name mismatch for {tier_name}")
        if summary.get("tier_name") != tier_name:
            fail(f"Summary tier_name mismatch for {tier_name}")

        summaries.append(
            {
                "tier_name": tier_name,
                "output_folder": str(tier_output_folder.resolve()),
                "verified_files": list(EXPECTED_TIER_FILES),
            }
        )
    return summaries


def run_example(example_path: Path, repo_root: Path, output_root: Path) -> dict:
    example_name = example_path.name
    data_module = importlib.import_module(f"examples.{example_name}.data")
    tier_module = importlib.import_module(f"examples.{example_name}.tier_structure")
    estimation_module = importlib.import_module(f"examples.{example_name}.estimation")

    estimation_mode = os.environ["RELEASE_VALIDATE_ESTIMATION_MODE"]
    settings_attr = {
        "fast": "FAST_TEST_ESTIMATION_SETTINGS",
        "end-to-end": "END_TO_END_ESTIMATION_SETTINGS",
    }[estimation_mode]
    if not hasattr(estimation_module, settings_attr):
        fail(f"Example {example_name} does not expose {settings_attr}")
    estimation_settings = getattr(estimation_module, settings_attr)

    output_folder = output_root / example_name
    output_folder.mkdir(parents=True, exist_ok=True)

    original_output_folder = tier_module.ESTIMATION_FOLDER
    tier_module.ESTIMATION_FOLDER = str(output_folder)

    try:
        data = data_module.load_data(str(example_path / "data"))
        multitier = tier_module.create_tier_structure(data, matlab_session="auto")
        estimation_module.run_multitier_estimation(
            multitier,
            estimation_settings=estimation_settings,
        )
        tier_summaries = verify_outputs(multitier, output_folder)
        return {
            "example_name": example_name,
            "estimation_mode": estimation_mode,
            "output_folder": str(output_folder.resolve()),
            "tier_summaries": tier_summaries,
        }
    finally:
        tier_module.ESTIMATION_FOLDER = original_output_folder


def main() -> int:
    repo_root = Path(os.environ["RELEASE_VALIDATE_REPO_ROOT"]).resolve()
    output_root = Path(os.environ["RELEASE_VALIDATE_OUTPUT_ROOT"]).resolve()
    examples_root = repo_root / "examples"

    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))

    package_path = verify_installed_package(repo_root)
    examples = discover_examples(examples_root)
    if not examples:
        fail(f"No examples discovered under {examples_root}")

    result = {
        "package_path": package_path,
        "examples": [],
    }
    for example_path in examples:
        result["examples"].append(run_example(example_path, repo_root, output_root))

    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
""".strip()
        + "\n",
        encoding="utf-8",
    )
    return runner_path


def run_examples(repo_root: Path, env_name: str, staging_root: Path, estimation_settings: str) -> dict[str, Any]:
    print_section("Run Examples")
    output_root = staging_root / "example_outputs"
    output_root.mkdir(parents=True, exist_ok=True)
    runner_path = write_runner_script(staging_root)
    env = os.environ.copy()
    env["RELEASE_VALIDATE_REPO_ROOT"] = str(repo_root)
    env["RELEASE_VALIDATE_OUTPUT_ROOT"] = str(output_root)
    env["RELEASE_VALIDATE_ESTIMATION_MODE"] = estimation_settings

    result = run_command(
        conda_python_command(env_name) + [str(runner_path)],
        cwd=repo_root,
        env=env,
    )

    json_start = result.stdout.find("{")
    if json_start == -1:
        raise ReleaseValidationError("Could not parse example validation JSON output.")
    return json.loads(result.stdout[json_start:])


def print_example_summary(example_results: dict[str, Any]) -> None:
    package_path = example_results["package_path"]
    print(f"Installed package path: {package_path}")
    for example in example_results["examples"]:
        print(f"Example {example['example_name']} ({example['estimation_mode']}): OK")
        print(f"  Output folder: {example['output_folder']}")
        for tier in example["tier_summaries"]:
            print(f"  Tier {tier['tier_name']}: verified {', '.join(tier['verified_files'])}")


def cleanup_staging(staging_root: Path, keep_artifacts: bool, success: bool) -> None:
    print_section("Cleanup")
    if keep_artifacts:
        print(f"Keeping validation artifacts at {staging_root}")
        return
    if not success:
        print(f"Validation failed. Preserving artifacts at {staging_root}")
        return
    shutil.rmtree(staging_root, ignore_errors=True)
    print(f"Removed temporary validation artifacts from {staging_root}")


def main() -> int:
    args = parse_args()
    repo_root = Path(__file__).resolve().parents[1]
    package_name, version = load_project_metadata(repo_root)
    examples = discover_examples(repo_root)
    staging_root = create_staging_root(repo_root, args.output_root)

    print_section("Release Validation")
    print(f"Package: {package_name}")
    print(f"Version: {version}")
    print(f"Target env: {args.env_name}")
    print(f"Estimation settings: {args.estimation_settings}")
    print(f"Examples discovered: {', '.join(example.name for example in examples)}")
    print(f"Staging root: {staging_root}")

    success = False
    try:
        wheel_path = build_wheel(repo_root, package_name, version)
        uninstall_previous_version(repo_root, args.env_name, package_name)
        install_wheel(repo_root, args.env_name, wheel_path)
        confirm_installed_version(repo_root, args.env_name, package_name, version)
        example_results = run_examples(repo_root, args.env_name, staging_root, args.estimation_settings)
        print_section("Verification Summary")
        print_example_summary(example_results)
        success = True
        print("\nRelease validation passed.")
        return 0
    except ReleaseValidationError as exc:
        print(f"\nRelease validation failed: {exc}", file=sys.stderr)
        return 1
    finally:
        cleanup_staging(staging_root, args.keep_artifacts, success)


if __name__ == "__main__":
    raise SystemExit(main())
