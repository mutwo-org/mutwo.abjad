# Change Log

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).

## [Unreleased]


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

