# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2019-02-09

### Added

### Changed

- Output structure on disk has been changed. A new directory level was added based on the input name. This was done in preparation to handle attachments and possible duplicate filenames.

### Removed

### Fixed

- Strong and emphasis text styles should now be preserved.
- Duplicate filenames (identical note title) are now handled correctly.


## [0.1.1] - 2019-02-05

### Added

### Changed

- Subsequent empty lines are compressed to one.

### Removed

### Fixed

- Lists are converted correctly. An empty line is forced before list items.
- Tasks are converted correctly to [GFM Task list items](https://github.github.com/gfm/#task-list-item).
- Tables created within Evernote are converted to [GFM Tables](https://github.github.com/gfm/#table).