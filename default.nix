let

  mutwo-nix-archive = builtins.fetchTarball "https://github.com/mutwo-org/mutwo-nix/archive/main.tar.gz";
  mutwo-abjad = import (mutwo-nix-archive + "/mutwo.abjad/default.nix");


in

  mutwo-abjad
