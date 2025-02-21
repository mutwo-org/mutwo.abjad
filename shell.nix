{
  # We use the same nixpkgs hash as mutwo-nix
  sources ? import ((fetchTarball "https://github.com/mutwo-org/mutwo-nix/archive/refs/heads/main.tar.gz") + "/nix/sources.nix"),
  pkgs ? import sources.nixpkgs {}
}:

let

  mutwoabjad = import ./default.nix;

  mypython = pkgs.python311.buildEnv.override {
    extraLibs = with pkgs.python311Packages; [
      mutwoabjad
      # Needed for mutwo.abjad tests
      pytest
      pillow
    ];
  };

in

  pkgs.mkShell {
      buildInputs = with pkgs; [
          mypython
          # Needed for mutwo.abjad tests
          lilypond-with-fonts
      ];
  }
