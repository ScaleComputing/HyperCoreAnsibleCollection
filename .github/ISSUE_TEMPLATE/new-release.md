---
name: New release
about: Start a new release
title: ":flying_saucer: Release version [VERSION]"
labels: release
assignees: shoriminimoe

---

The new release version is **[VERSION]**

## Release steps

Please complete these steps in order.

- [ ] Update the top-level README.md with links to new modules (run `./docs/helpers/generate_readme_fragment.py`)
- [ ] Update the version number in galaxy.yml e.g. `1.1.1`
- [ ] Update the changelog with `antsibull-changelog` e.g. `antsibull-changelog release --version 1.1.1`
- [ ] Update the list of supported HyperCore versions in the README and in `docs/rst/index.rst`
- [ ] Tag the commit with the version number prefixed with 'v' e.g. `v1.1.1`
- [ ] Deploy new documentation using gh-pages - "Deploy static content to Pages"
