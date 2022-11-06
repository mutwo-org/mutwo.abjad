with import <nixpkgs> {};
with pkgs.python310Packages;

let

  mutwo-core-archive = builtins.fetchTarball "https://github.com/mutwo-org/mutwo.core/archive/61ebb657ef5806eb067f5df6885254fdbae8f44c.tar.gz";
  mutwo-core = import (mutwo-core-archive + "/default.nix");

  mutwo-music-archive = builtins.fetchTarball "https://github.com/mutwo-org/mutwo.music/archive/d90b6db7d433d64c25f039adcd6b41075c05c013.tar.gz";
  mutwo-music = import (mutwo-music-archive + "/default.nix");

  mutwo-ekmelily-archive = builtins.fetchTarball "https://github.com/mutwo-org/mutwo.ekmelily/archive/6d30ef1f7c5a51ff86d16c0d81e6b2b7bc0a72ab.tar.gz";
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
      rev = "f2d0fc9c50ba8a10420dbfb4cc7240e093c30e87";
      sha256 = "sha256-MrkGsqCM1E56MTpkB9VaY0CKYnCv7zrLULoWmc9p3Sg=";
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
