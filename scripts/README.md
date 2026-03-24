# Scripts

## Release validation

Run the pre-publish package validation script from the repository root:

```powershell
conda run -n debtoolpyif_dev python scripts\release_validate.py
```

This script:

- builds the current wheel from `pyproject.toml`
- uninstalls the previous package from `debtoolpyif_test`
- installs the newly built wheel into `debtoolpyif_test`
- runs all discovered examples with their fast estimation settings
- verifies the expected result files for each tier
- cleans temporary validation outputs on success

Useful options:

```powershell
conda run -n debtoolpyif_dev python scripts\release_validate.py --keep-artifacts
conda run -n debtoolpyif_dev python scripts\release_validate.py --env-name my_test_env
conda run -n debtoolpyif_dev python scripts\release_validate.py --output-root tmp\release_checks
```
