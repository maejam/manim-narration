# The other python versions 'testall' should run on.
TESTALL_VERSIONS := "3.10 3.11 3.12"


set shell := ["uv", "run", "bash", "-euo", "pipefail", "-c"]


# Main python version
python_version := `uv run python -c 'import platform; print(platform.python_version())'`


# string formatting variables
bold := `tput bold`
normal := `tput sgr0`


# The default recipe: run all qa tools on file(s)
qa *files: (format files) (check files) (type files) (test files) coverage

# Format file(s) using ruff
[no-exit-message]
format *files:
    ruff format {{files}}

# Lint file(s) using ruff
[no-exit-message]
check *files:
    ruff check {{files}}

# Type check file(s) using mypy
[no-exit-message]
type *files:
    mypy {{files}}

# Run tests on file(s) using pytest
[no-exit-message]
test *files: (_test python_version files)

[no-exit-message]
_test version *files:
    #!/usr/bin/env bash
    set -euo pipefail
    printf "{{bold}}pytest {{files}} (python {{version}}){{normal}}\n"
    if [[ {{version}} = {{python_version}} ]]; then
        cmd="uv run coverage run -m pytest --color=yes {{files}}"
    else
        cmd="uv run --python {{version}} pytest --color=yes {{files}}"
    fi
    eval "$cmd" || {
        # Do not block commits if no tests to run
        if [[ $? = 5 ]]; then
            printf "⚠️  No tests to run!\n"
            exit 0
        else
            exit 1
        fi
    }

# Display the code coverage
[no-exit-message]
coverage mode="report":
    #!/usr/bin/env bash
    set -euo pipefail
    printf "{{bold}}coverage{{normal}}\n"
    output=$(uv run coverage {{mode}}) || {
        # Do not block commits if no data to report
        if [[ "$output" =~ "No data to report" ]]; then
            printf "⚠️  No data to report. Run the tests first!\n"
            exit 0
        else
            printf "$output"
            exit 1
        fi
    }
    uv run coverage {{mode}}
    exit 0

# Run your tests with all python versions
[no-exit-message]
testall *files:
    #!/usr/bin/env bash
    set -euo pipefail
    for version in {{TESTALL_VERSIONS}}; do
        just _test "$version" {{files}}
    done

# The content to write in the pre-commit file
# https://github.com/casey/just?tab=readme-ov-file#printing-complex-strings
export PRECOMMIT := '''
    #!/usr/bin/env bash
    set -euo pipefail

    ##### Run all qa tools on added, copied or modified files in the git index #####

    files=$(git diff --cached --name-only --diff-filter=ACM | grep ".py$" || true)

    # Only run those tools on python files
    if [[ -n "$files" ]]; then
        just format $files
        just check $files
        # Don't run mypy on tests and examples
        tocheck=()
        for file in $files; do
            if [[ "$file" != tests/* && "$file" != examples/* ]]; then
                tocheck+=("$file")
            fi
        done
        if (( ${#tocheck[@]} != 0 )); then
            just type ${tocheck[@]}
        fi
    fi

    # Run these no matter what
    just testall
    just test
    just coverage


'''

# Install the pre-commit hook into git repo
install-hook:
    #!/usr/bin/env bash
    set -euo pipefail
    if [ ! -f .git/hooks/pre-commit ]; then
        printf %s "$PRECOMMIT" > .git/hooks/pre-commit
        chmod +x .git/hooks/pre-commit
        printf "✅ pre-commit hook successfully installed!\n"
    else
        printf "⚠️  The file .git/hooks/pre-commit already exists.\n"
    fi
