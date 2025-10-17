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


####################################################################
# The recipes below are taken from:                                #
# https://github.com/alltuner/uv-version-bumper/blob/main/justfile #
####################################################################

# Bump version by patch and create git tag
bump-patch:
    @just bump-and-tag patch

# Bump version by minor and create git tag
bump-minor:
    @just bump-and-tag minor

# Bump version by major and create git tag
bump-major:
    @just bump-and-tag major

# Internal recipe to bump version and create git tag
bump-and-tag type:
    #!/usr/bin/env bash
    # Check if the repo is clean
    if [[ -n $(git status --porcelain) ]]; then
        echo "Error: Git repository has uncommitted changes. Please commit or stash them first."
        exit 1
    fi
    
    # Get the current version before bumping
    OLD_VERSION=$(uv version --short)
    echo "Current version: $OLD_VERSION"
    
    # Bump the version
    echo "Bumping {{ type }} version..."
    uv version --bump {{ type }}
    
    # Get the new version
    NEW_VERSION=$(uv version --short)
    echo "New version: $NEW_VERSION"
    
    # Run uv sync to update the lock file
    echo "Updating lock file with uv sync..."
    uv sync
    
    # Commit both the pyproject.toml and lock file changes in one commit
    git add pyproject.toml
    git add .
    git commit -m "build: bump version: $OLD_VERSION → $NEW_VERSION"
    
    # Create tag directly rather than calling another recipe
    VERSION=$NEW_VERSION
    TAG="v$VERSION"
    
    # Check if tag already exists
    if git rev-parse "$TAG" >/dev/null 2>&1; then
        echo "Tag $TAG already exists. Skipping tag creation."
    else
        echo "Creating git tag $TAG..."
        git tag -a "$TAG" -m "Version $VERSION"
        echo "Created git tag: $TAG"
        echo "To push the tag, run: git push origin $TAG"
    fi

# Create git tag from current version if it doesn't exist
tag-version:
    #!/usr/bin/env bash
    VERSION=$(uv version --short)
    TAG="v$VERSION"
    
    # Check if tag already exists
    if git rev-parse "$TAG" >/dev/null 2>&1; then
        echo "Tag $TAG already exists. Skipping tag creation."
    else
        echo "Creating git tag $TAG..."
        git tag -a "$TAG" -m "Version $VERSION"
        echo "Created git tag: $TAG"
        echo "To push the tag, run: git push origin $TAG"
    fi

# Push the latest version tag to remote
push-tag:
    #!/usr/bin/env bash
    VERSION=$(uv version --short)
    TAG="v$VERSION"
    
    # Check if tag exists locally
    if git rev-parse "$TAG" >/dev/null 2>&1; then
        echo "Pushing tag $TAG to remote..."
        git push origin "$TAG"
        echo "Tag $TAG pushed successfully!"
    else
        echo "Tag $TAG does not exist locally. Create it first with 'just tag-version'."
        exit 1
    fi

# Push both commits and tag to remote
push-all:
    #!/usr/bin/env bash
    VERSION=$(uv version --short)
    TAG="v$VERSION"
    
    # Push commits
    echo "Pushing commits to remote..."
    git push
    
    # Check if tag exists locally
    if git rev-parse "$TAG" >/dev/null 2>&1; then
        echo "Pushing tag $TAG to remote..."
        git push origin "$TAG"
        echo "All changes pushed successfully!"
    else
        echo "Tag $TAG does not exist locally. Create it first with 'just tag-version'."
        exit 1
    fi

# Show current version
version:
    @uv version --short
