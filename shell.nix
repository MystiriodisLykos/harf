{ pkgs ? import <nixpkgs> {} }:

with pkgs;
let
    pyserde = python39Packages.buildPythonPackage rec {
        pname = "pyserde";
        version = "0.7.2";
        src = python39Packages.fetchPypi {
            inherit pname version;
            sha256 = "0qnv3b06a797yhdz2wflnkh1q22b4nspny9z0kdikqlpj4gz3gqj";
        };
        propagatedBuildInputs = [
            python39Packages.typing-inspect
            python39Packages.jinja2
            python39Packages.stringcase
        ];
        doCheck = false;
    };
    mypython = python310.buildEnv.override {
        extraLibs = with python39Packages; [
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
