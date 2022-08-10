{ lib, buildPythonPackage, pyserde }:

buildPythonPackage rec {
    pname = "harf";
    version = "0.0.1";
    
    src = ./src;

    propagatedBuildInputs = [ pyserde ];
}
