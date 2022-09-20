{ lib, buildPythonPackage, pyserde, click, hypothesis, pytestCheckHook }:

buildPythonPackage rec {
    pname = "harf";
    version = "0.0.1";
    
    src = ./.;

    propagatedBuildInputs = [ pyserde click ];

    checkInputs = [ pytestCheckHook hypothesis ];
    pythonImportsCheck = ["harf.cli"];
    pytestFlagsArray = [ "--hypothesis-show-statistics" ];
}
