# Change Log

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).

## [Unreleased]

## [0.20.0] - 2024-04-26

This update 'mutwo.abjad' to new major 'mutwo.core' version.

### Changed
- `TempoEnvelopeToAbjadAttachmentTempo` to `TempoToAbjadAttachmentTempo`
- `ComplexTempoEnvelopeToAbjadAttachmentTempo` to `ComplexTempoToAbjadAttachmentTempo`
- `NestedComplexEventToAbjadContainer` to `NestedCompoundToAbjadContainer`
- `NestedComplexEventToComplexEventToAbjadContainers` to `NestedCompoundToCompoundToAbjadContainers`
- `CycleBasedNestedComplexEventToComplexEventToAbjadContainers` to `CycleBasedNestedCompoundToCompoundToAbjadContainers`
- `TagBasedNestedComplexEventToComplexEventToAbjadContainers` to `TagBasedNestedCompoundToCompoundToAbjadContainers`
- `SequentialEventToAbjadVoice` to `ConsecutionToAbjadVoice`
- `SequentialEventToQuantizedAbjadContainer` to `ConsecutionToQuantizedAbjadContainer`
- `LeafMakerSequentialEventToQuantizedAbjadContainer` to `LeafMakerConsecutionToQuantizedAbjadContainer`
- `NauertSequentialEventToQuantizedAbjadContainer` to `NauertConsecutionToQuantizedAbjadContainer`


## [0.19.0] - 2024-01-08

### Added
- support for newer abjad version


## [0.18.0] - 2023-12-27

### Added
- `abjad_parameters.Slur`, see [here](https://github.com/mutwo-org/mutwo.abjad/commit/796acf26ca7f2b53e470c938d15dc0e44fdabdcc)

### Changed
- make tests more reliable, see [here](https://github.com/mutwo-org/mutwo.abjad/commit/6b36baedd1f206a61081bd672650f76f35fdfb23)


## [0.17.0] - 2023-12-19

### Added
- `abjad_utilities.concatenate_adjacent_tuplets`, see [here](https://github.com/mutwo-org/mutwo.abjad/commit/2af2c1ec192962eb97998e027a77740dc7cbfcb0)
- option `concatenate_adjacent_tuplets` to `LeafMakerSequentialEventToQuantizedAbjadContainer`, see [here](https://github.com/mutwo-org/mutwo.abjad/commit/0d379524ea87c3eb57e1132b0b59a3c1e5b8289a)
- `abjad_utilities.reduce_multiplier`, see [here](https://github.com/mutwo-org/mutwo.abjad/commit/1d35c04d7f1a939f4de54731e7424e172852ff65)
- option `reduce_multiplier` to `LeafMakerSequentialEventToQuantizedAbjadContainer`, see [here](https://github.com/mutwo-org/mutwo.abjad/commit/7d532a6094b17f1a773bc460b0fa9754f2ed8c75)

### Changed
- Set default quantizer to `LeafMakerSequentialEventToQuantizedAbjadContainer`, see [here](https://github.com/mutwo-org/mutwo.abjad/commit/a207dc4454dcd70a19376d7d2749e1fd8bfd9804)
- Move `is_simple_event_rest` argument from `SequentialEventToAbjadVoice` to `SequentialEventToQuantizedAbjadContainer`, see [here](https://github.com/mutwo-org/mutwo.abjad/commit/f83878edb642a9b81b8a2a3dca0c4f3d2544d05a)


## [0.16.0] - 2023-06-08

### Fixed
- conversion of microtonal `WesternPitch`
- fermata attachment on multimeasure rest (disappeared before)
- printing of duration lines for both natural harmonic items
- string contact point which was sometimes written below the staff instead of above the staff

### Added
- `duration_line_engraver` and `prepare_for_duration_line_based_notation` arguments for `SequentialEventToAbjadVoice` for more flexible duration line based setups


## [0.15.0] - 2023-01-08

### Added
- `with_duration_line` attribute to all abjad attachments

### Fixed
- natural harmonic node list indicator for duration line based notation
- duplicate indicators for double harmonics


## [0.14.0] - 2022-12-31

### Added
- `replace_leaf_by_leaf` property for all abjad attachments
- `NaturalHarmonicNodeList` attachment

### Changed
- internal structure of abjad attachments: see [here](https://github.com/mutwo-org/mutwo.abjad/commit/7a6dcfb3969349a3c867bf808f214e005a0bd472).

### Removed
- `NaturalHarmonic` attachment
- `PreciseNaturalHarmonic` attachment


## [0.13.0] - 2022-11-08

### Added

#### `abjad_converters.SequentialEventToQuantizedAbjadContainer`
- `event_to_tempo_envelope` argument in init
- `event_to_time_signature_tuple` argument in init

#### `abjad_converters.SequentialEventToAbjadVoice`
- `default_tempo_envelope` to init
- `event_to_tempo_envelope` to init

### Changed
#### `abjad_converters.SequentialEventToQuantizedAbjadContainer`
- `time_signature_sequence` argument to `default_time_signature_sequence`

### Removed
#### `abjad_converters.SequentialEventToQuantizedAbjadContainer`
- `tempo_envelope` argument


## [0.12.0] - 2022-11-06

### Dropped
- python 3.9 support

### Changed
- from abjad 3.4 to abjad 3.7 (actually abjad 3.7 is the last version which support lilypond 2.22.X)


## [0.11.0] - 2022-08-10

### Changed
- `mutwo.ext-abjad` to `mutwo.abjad`
- `expenvelope.Envelope` to `core_events.TempoEnvelope`


## [0.10.0] - 2022-06-12

### Changed
- `abjad_converters.RMakersSequentialEventToQuantizedAbjadContainer` to `abjad_converters.LeafMakerSequentialEventToQuantizedAbjadContainer`
- `abjad_converters.RMakersSequentialEventToDurationLineBasedQuantizedAbjadContainer` to `abjad_converters.LeafMakerSequentialEventToDurationLineBasedQuantizedAbjadContainer`

### Fixed
- quantization of very long leafs by `abjad_converters.LeafMakerSequentialEventToQuantizedAbjadContainer`

### Removed
- `abjad-ext-rmakers` dependency

### Added
- monkey patches for `abjad` in `mutwo_third_party/abjad`


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

