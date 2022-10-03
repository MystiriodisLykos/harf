{ lib, buildPythonPackage, pyserde, click, hypothesis, pytestCheckHook }:

buildPythonPackage rec {
    format = "pyproject";

    pname = "harf";
    version = "0.0.2";
    
    src = ./.;

    propagatedBuildInputs = [ pyserde click ];

    checkInputs = [ pytestCheckHook hypothesis ];
    pythonImportsCheck = ["harf.cli"];
    pytestFlagsArray = [ "--hypothesis-show-statistics" ];
}
