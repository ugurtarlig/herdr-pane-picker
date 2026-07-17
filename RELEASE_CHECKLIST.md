# Release checklist

## Before publishing

- [ ] Review `README.md`, plugin ID, version, and MIT attribution.
- [ ] Review every documentation image for content that should not be public
      (secrets, credentials, work data, third-party names). Personal workspace
      content is acceptable when deliberately chosen; the fictional demo layout
      (`scripts/demo_layout.py`) remains available for fully impersonal captures.
- [ ] Confirm the portable popup action selects and cancels correctly.
- [ ] Confirm the popup-free WezTerm action selects, cancels, and falls back to native `PaneSelect` outside Herdr.
- [ ] Run `python3 -m unittest discover -s tests -v`.
- [ ] Run `python3 -m compileall -q pane_picker.py scripts tests`.
- [ ] Validate the local WezTerm module with a temporary configuration.
- [ ] Run a personal-string and secret scan over tracked files.

## Publish

```sh
git commit -m "feat: release Herdr Pane Picker 0.1.0"

gh repo create ugurtarlig/herdr-pane-picker \
  --public \
  --source=. \
  --remote=origin \
  --description "Pick a Herdr pane by typing its on-pane character hint"

git push -u origin main
git tag -a v0.1.0 -m "Herdr Pane Picker 0.1.0"
git push origin v0.1.0

gh repo edit ugurtarlig/herdr-pane-picker \
  --add-topic herdr-plugin \
  --add-topic herdr \
  --add-topic wezterm \
  --add-topic terminal
```

## Verify

```sh
herdr plugin install ugurtarlig/herdr-pane-picker --ref v0.1.0
herdr plugin list --plugin ugurtarlig.pane-picker
herdr plugin action invoke ugurtarlig.pane-picker.open
```

- [ ] Create the GitHub release from tag `v0.1.0`.
- [ ] Confirm the repository description and topics.
- [ ] Confirm the plugin appears on https://herdr.dev/plugins/ after the marketplace refresh.
