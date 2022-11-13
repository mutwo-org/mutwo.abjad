with import <nixpkgs> {};
with pkgs.python310Packages;

let

  mutwo-core-archive = builtins.fetchTarball "https://github.com/mutwo-org/mutwo.core/archive/83efe12fb98119e03db833c231f9c87956577b3f.tar.gz";
  mutwo-core = import (mutwo-core-archive + "/default.nix");

  mutwo-music-archive = builtins.fetchTarball "https://github.com/mutwo-org/mutwo.music/archive/6a5f2ca81e6e4e06b7ad4d6f46b0361ceaca4ea1.tar.gz";
  mutwo-music = import (mutwo-music-archive + "/default.nix");

  mutwo-ekmelily-archive = builtins.fetchTarball "https://github.com/mutwo-org/mutwo.ekmelily/archive/e466119683d076b60c7e65b2570fdefc8382fe3a.tar.gz";
  mutwo-ekmelily = import (mutwo-ekmelily-archive + "/default.nix");

  quicktions = pkgs.python310Packages.buildPythonPackage rec {
    name = "quicktions";
    src = fetchPypi {
      pname = name;
      version = "1.13";
      sha256 = "sha256-HzmMN1sAUjsSgy7vNvX/hq49LZmSnTQYbamjRoXeaL0=";
    };
    doCheck = true;
    propagatedBuildInputs = [
      python310Packages.cython_3
      python310Packages.codecov
    ];
  };

  sphinx-autodoc-typehints = pkgs.python310Packages.buildPythonPackage rec {
    name = "sphinx-autodoc-typehints";
    src = fetchPypi {
      pname = "sphinx_autodoc_typehints";
      version = "1.18.3";
      sha256 = "sha256-wE2PjXDpiJYOJbIGrzmpDfhOfiwIW7JOEjvDaEAhsxM=";
    };
    propagatedBuildInputs = [
      python310Packages.sphinx
    ];
    doCheck = true;
  };

  ply = pkgs.python310Packages.buildPythonPackage rec {
    name = "ply";
    src = fetchFromGitHub {
      owner = "dabeaz";
      repo = name;
      rev = "0f398b72618c1564d71f7dc0558e6722b241875a";
      sha256 = "sha256-PEwIgmM7DQHy6FOhcUwkricrdW3wZe3ggSQnUvgKISo=";
    };
    doCheck = true;
  };

  uqbar = pkgs.python310Packages.buildPythonPackage rec {
    name = "uqbar";
    src = fetchPypi {
      pname = name;
      version = "0.5.9";
      sha256 = "sha256-0G02Amj8qB81DD0E1whPNYq9xfU6JeXrKuEW8F9HhQY=";
    };
    propagatedBuildInputs = [
      python310Packages.sphinx_rtd_theme
      python310Packages.flake8
      python310Packages.isort
      python310Packages.mypy
      python310Packages.pytest
      python310Packages.pytest-cov
      python310Packages.unidecode
      python310Packages.sphinx
      python310Packages.black
      sphinx-autodoc-typehints
    ];
    doCheck = false;
  };

  abjad = pkgs.python310Packages.buildPythonPackage rec {
    name = "abjad";
    src = fetchPypi {
      pname = name;
      version = "3.7";
      sha256 = "sha256-3N/Z6UgBG8Wi+hWKvuBWss42rlwaivsmHlrfr+Y8/us=";
    };
    patchPhase = ''
        # Remove useless sphinx-autodoc-typehints dependency.
        #     (we don't need to build docs here)
        # See:
        #   https://github.com/Abjad/abjad/blob/v3.7/setup.py#L84
        sed -i '84d' setup.py
    '';
    propagatedBuildInputs = [
      quicktions
      uqbar
      ply
      python310Packages.black
      python310Packages.flake8
      python310Packages.isort
      python310Packages.mypy
      python310Packages.pytest
      python310Packages.pytest-cov
      python310Packages.roman
      python310Packages.six
      python310Packages.pytest-helpers-namespace
    ];
    doCheck = false;
  };

  abjad-ext-nauert = pkgs.python310Packages.buildPythonPackage rec {
    name = "abjad-ext-nauert";
    src = fetchPypi {
      pname = name;
      version = "3.7";
      sha256 = "sha256-+RHZPQQPNCv2AJKHX+8YEif4ZFS/2XuUO17EsY+Qg5Q=";
    };
    doCheck = true;
    propagatedBuildInputs = [
      abjad
    ];
  };

  # Fix Fontconfig error: Cannot load default config file
  fontsConf = makeFontsConf {
    fontDirectories = [ freefont_ttf ];
  };

  # Fix Fontconfig error: Can't find cache
  fontsCache= makeFontsCache {};

in

  buildPythonPackage rec {
    name = "mutwo.abjad";
    src = fetchFromGitHub {
      owner = "mutwo-org";
      repo = name;
      rev = "861d157c4d94fd2e1dab920c47f29581fe05ee99";
      sha256 = "sha256-u1QB35BFUPT4mfk3ZyI8Df0/lGnT37oKW1xXis7QOu8=";
    };
    checkInputs = [
      python310Packages.pytest
      python310Packages.pillow
      lilypond-with-fonts
    ];
    propagatedBuildInputs = [
      abjad
      abjad-ext-nauert
      mutwo-core
      mutwo-music
      mutwo-ekmelily
      lilypond-with-fonts
    ];
    checkPhase = ''
      runHook preCheck
      export FONTCONFIG_FILE=${fontsConf};
      pytest
      runHook postCheck
    '';
    doCheck = true;
    build-cache-failures = true;
  }