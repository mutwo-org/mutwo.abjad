let
  sourcesTarball = fetchTarball "https://github.com/mutwo-org/mutwo-nix/archive/refs/heads/main.tar.gz";
  mutwo-abjad = import (sourcesTarball + "/mutwo.abjad/default.nix") {};
  mutwo-abjad-local = mutwo-abjad.overrideAttrs (
    finalAttrs: previousAttrs: {
       src = ./.;
    }
  );
in
  mutwo-abjad-local
