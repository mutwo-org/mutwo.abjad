# Change Log

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).

## [Unreleased]


## [0.9.0] - 2022-05-02

### Changed
- `Hairpin` attachment
- changed bad converter names (XToYConverter -> XToY)


## [0.8.0] - 2022-04-18

### Added
- Cue and WoodwindFinger attachment classes


## [0.7.0] - 2022-04-18

### Changed
- updated to new `mutwo.ext-music` and `mutwo.ext-ekmelily` versions


## [0.4.0] - 2022-04-03

### Added
- conversion of lyrics

### Changed
- internal structure


## [0.3.0] - 2022-03-23

### Changed
- split `constants` to `configurations` / `constants`

## [0.3.0] - 2022-03-05

### Changed
- package structure to namespace package to apply refactor of mutwo main package
- default arguments (lambda functions) in `SequentialEventToAbjadVoiceConverter` to common `music_converters` functions
- moved `attachments` from `converters` to `abjad_parameters`
- `...Converter` to `...`, for instance:
    - `SequentialEventToAbjadVoiceConverter` to `SequentialEventToAbjadVoice`
    - `MutwoPitchToAbjadPitchConverter` to `MutwoPitchToAbjadPitch`
    - `MutwoVolumeToAbjadAttachmentDynamicConverter` to `MutwoVolumeToAbjadAttachmentDynamic`
    - `TempoEnvelopeToAbjadAttachmentTempoConverter` to `TempoEnvelopeToAbjadAttachmentTempo`
    - ...


## [0.2.0] - 2022-01-11

### Changed
- applied movement from music related parameter and converter modules (which have been moved from [mutwo core](https://github.com/mutwo-org/mutwo) in version 0.49.0 to [mutwo.ext-music](https://github.com/mutwo-org/mutwo.ext-music))

