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
    mypython = python3.buildEnv.override {
        extraLibs = with python3Packages; [
            mypy
            black
            pyserde
        ];
    };

    myvim = let
            common_vim = import /etc/nixos/common_vim.nix;
        in (vim_configurable.override { python = python3; }).customize {
            name = common_vim.name;
            vimrcConfig.customRC = common_vim.vimrcConfig.customRC + ''
                set foldmethod=syntax
                nnoremap <space> za

                set encoding=utf-8
                set nospell
            '';
        };
in

pkgs.mkShell {
    buildInputs = [
        mypython
        myvim
    ];
}
