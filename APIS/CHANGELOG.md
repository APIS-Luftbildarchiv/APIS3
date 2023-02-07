# Changelog
All notable changes to APIS4QGIS3 project will be documented in this file.

## [Unreleased]
### [3.5.0] Multilanguage
- Multilanguage
### [3.4.0] Chronolgoy
- Chronology
### [3.3.2] Sites and Findspots
- ExportFSWithFO
- EditingFSChangeFO
### [3.3.1] Interpretation
- InterpretationsLoading
### [3.3.0] Representative Images
- RepresenativeImagesFile
- MultipleRepresentativeImagesFOs
- RepresentativeImageFS
## [3.2.0-alpha.0] Bundesheer
- Bundesheer Add-On.
- ImageEditVertical
- Missing for 3.2.0: Procedure for data exchange & integration (+ finalizing integration of existing BH data)
## [3.1.4] - 2021-08-19
#### Fixed
- ident zu 3.1.3 (bug fix Installationsproblem)
## [3.1.3] - 2020-10-22
### Added
- SystemTableEditor
- OrientALUpdate / Digital Image Autoimporter
### Fixed
- Vertical image mapping (footprint generation): kappa (azimuth) for each image is written to center point layer on footprint creation.
## [3.1.2] - 2020-03-05
### Fixed
- Datierungs Quelle is now a mandatory field in the findspot dialog.
- Bug that caused to not show the representative aerial image.
- Site dialog in the findspot table: column Periode Detail instead of Periode is shown.
- Bug in Mosaic Loading fixed (The search string for mosaic filenames also captured orthofotos not following standard naming).
## [3.1.1] - 2020-01-20
### Added
- Site (Fudort) editing allows to use a Geometry from a Layer loaded in QGIS (Single Selection only!) to map a site. For example, can be used to re-map sites outside of Austria, that still have an AUT.* Id.
- Loading Ortho Mosaics: Extension of Image Registry and integration in the Image Selection List Dialog. When available, the mosaic will be loaded into QGIS when loading Orthofotos for the listed/selected images.
### Changed
## [3.1.0] - 2020-01-10
### Changed
- Porting of APIS2 (QGIS2, PyQGIS2, PyQt5) to APIS3 (QGIS3, PyQGIS3, PyQt5)
## [3.0.1] - 2019-01-08
### Fixed
- ...
## [3.0.0] - 2019-01-07
### Changed
- Porting of APIS2 (QGIS2, PyQGIS2, PyQt5) to APIS3 (QGIS3, PyQGIS3, PyQt5)
<!--
## [0.0.0] - 20XX-12-30
### Added
- for new features.
### Changed
- for changes in existing functionality.
### Deprecated
- for once-stable features removed in upcoming releases.
### Removed
- for deprecated features removed in this release.
### Fixed
- for any bug fixes.
### Security
- to invite users to upgrade in case of vulnerabilities.
-->