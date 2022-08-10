{ pkgs ? import <nixpkgs> {} }:

with pkgs;
let
    pyserde = python3Packages.buildPythonPackage rec {
        pname = "pyserde";
        version = "0.7.2";
        src = python3Packages.fetchPypi {
            inherit pname version;
            sha256 = "0qnv3b06a797yhdz2wflnkh1q22b4nspny9z0kdikqlpj4gz3gqj";
        };
        propagatedBuildInputs = [
            python3Packages.typing-inspect
            python3Packages.jinja2
            python3Packages.stringcase
        ];
        doCheck = false;
    };
    harf = callPackage ./harf.nix {
        buildPythonPackage = python3Packages.buildPythonPackage;
        pyserde = pyserde;
    };
    mypython = python3.buildEnv.override {
        extraLibs = with python3Packages; [
            mypy
            black
            harf
        ];
    };

    myvim = (vim_configurable.override { python = python3; }).customize {
            name = "vim";
            vimrcConfig.customRC = ''
                set foldmethod=syntax
                nnoremap <space> za

                set encoding=utf-8
                set nospell
		set number relativenumber
		syntax on

		set tabstop=8 softtabstop=0 expandtab shiftwidth=4 smarttab
            '';
        };
in

pkgs.mkShell {
    buildInputs = [
        mypython
        myvim
    ];
}
