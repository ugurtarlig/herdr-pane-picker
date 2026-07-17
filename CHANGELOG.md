# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed

- The demo layout now creates its own `pane-picker-demo` tab instead of
  replacing the active tab, refuses to run against the default session, and
  gains a `--close` teardown flag. Previously it could destroy a real layout,
  and closing the last demo pane closed the user's tab with it.
- Demo panes now end on any keypress and on stdin EOF, in addition to
  SIGINT/SIGTERM/SIGHUP. A signal wakeup pipe closes a race where a
  termination signal could arrive before the pane blocked on input and be
  lost until the next keypress.

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
