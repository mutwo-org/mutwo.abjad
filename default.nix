with import <nixpkgs> {};
with pkgs.python310Packages;

let

  mutwo-core-archive = builtins.fetchTarball "https://github.com/mutwo-org/mutwo.core/archive/28a13e348876fa07929f5fd4f3953fee624c255c.tar.gz";
  mutwo-core = import (mutwo-core-archive + "/default.nix");

  mutwo-music-archive = builtins.fetchTarball "https://github.com/mutwo-org/mutwo.music/archive/725462d2342b0a27d88a38272b0ad93848d87399.tar.gz";
  mutwo-music = import (mutwo-music-archive + "/default.nix");

  mutwo-ekmelily-archive = builtins.fetchTarball "https://github.com/mutwo-org/mutwo.ekmelily/archive/5344389ebd60ffe91671e36094d873ce532a90b7.tar.gz";
  mutwo-ekmelily = import (mutwo-ekmelily-archive + "/default.nix");

  quicktions = pkgs.python310Packages.buildPythonPackage rec {
    name = "quicktions";
    src = fetchPypi {
      pname = name;
      version = "1.10";
      sha256 = "sha256-Oy072x22dBvFHOHbmmWdkcUpdCC5GmIAnILJdKNlwO4=";
    };
    doCheck = true;
    propagatedBuildInputs = [
      python310Packages.cython
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
      version = "0.4.8";
      sha256 = "sha256-Jb+rQ7XWflB2KyHaSfx9hDlAa3yjGwY/PjQpmUnxpeY=";
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
      version = "3.4";
      sha256 = "sha256-yXohy0IMIzLYazjcCCWx3zTjWAM+oMc4TK3XNyapFno=";
    };
    propagatedBuildInputs = [
      quicktions
      sphinx-autodoc-typehints
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
      version = "3.4";
      sha256 = "sha256-3fWr1Q/lFnuFRXnvulJDrwlWI3WCeEA8bEngdUZv1yo=";
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
      rev = "53a7ffd8112d2ae1097dd3c59eebf9df03c3d917";
      sha256 = "sha256-GDI5vi6JTygZ0U0zSyOdneT+x81XyFBMn4dtCZ9JRYg=";
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
