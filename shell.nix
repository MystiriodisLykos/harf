{ pkgs ? import <nixpkgs> {} }:

with pkgs;
let
    pyserde = python38Packages.buildPythonPackage rec {
        pname = "pyserde";
        version = "0.6.0";
        src = python39Packages.fetchPypi {
            inherit pname version;
            sha256 = "1d185la83r7w67vj5dss3khhz253czpjcnrcjqzyh9j6habxp3s2";
        };
        propagatedBuildInputs = [
            python38Packages.typing-inspect
            python38Packages.jinja2
            python38Packages.stringcase
        ];
        doCheck = false;
    };
    mypython = python38.buildEnv.override {
        extraLibs = with python38Packages; [
            mypy
            black
            markdown
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
