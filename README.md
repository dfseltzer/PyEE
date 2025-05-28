# PyEE
Python library for electrical engineering.  A bunch of helpers and convenience functions... some json files with useful data, and some models for common converters.

A collection of bits and pieces that have always come in handy to help let Python take the place of expensive software.

# Notes...

VSCode relative imports suck.  If re-installing, try...

## pyproject.toml

> [tool.pyright] \
> typeCheckingMode = "basic" \
> verboseOutput = "true" \
> extraPaths = [".", "pyee", "./pyee"]

## settings.json

> "python.autoComplete.extraPaths": [\
> "\${workspaceFolder}/pyee",\
> "\${workspaceFolder}"\
> "~/code/pyee"\
>]

## Terminal
make sure venv is active
> python -m pip install -e .