# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-07-17

### Added

- Home-row-first character hints drawn directly over panes.
- Portable Herdr popup action for terminal-independent key capture.
- Optional popup-free WezTerm integration with native `PaneSelect` fallback.
- Pre-rendered rounded PNG badges with a dependency-free RGBA fallback.
- Automatic overlay cleanup and structured local error logging.
- Fictional demo layout for privacy-safe documentation screenshots.

### Changed

- Send graphics updates sequentially to avoid local-socket contention and show
  four badges in approximately 5–7 ms on the reference system.

[Unreleased]: https://github.com/ugurtarlig/herdr-pane-picker/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/ugurtarlig/herdr-pane-picker/releases/tag/v0.1.0
