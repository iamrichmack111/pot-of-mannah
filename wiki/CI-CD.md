# CI/CD

Pot of Mannah uses GitHub Actions for four separate concerns.

## CI

`.github/workflows/ci.yml`

- Python matrix tests
- `pytest`
- Python compile checks
- food database verification
- Flask route smoke test
- Docker build validation

## Playwright Media

`.github/workflows/playwright-media.yml`

- creates a disposable demo database
- starts the Flask app
- installs Chromium
- captures seven screenshots
- records a guided browser demo
- stores media as an Actions artifact
- commits refreshed media to the repository

## Container

`.github/workflows/container.yml`

Builds and publishes `linux/amd64` and `linux/arm64` images to GitHub Container Registry.

## Release

`.github/workflows/release.yml`

A `v*` tag creates a GitHub Release and source ZIP. The existing PyPI workflow can then publish the Python package when the release is published.

## Wiki

`.github/workflows/wiki.yml`

Synchronizes Markdown pages under `wiki/` to the GitHub Wiki repository.
