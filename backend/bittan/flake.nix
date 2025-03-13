{
  description = "Python venv development template";

  inputs = {
    utils.url = "github:numtide/flake-utils";
  };


  outputs = {
    self,
    nixpkgs,
    utils,
    ...
  }:
    utils.lib.eachDefaultSystem (system: let
      pkgs = import nixpkgs {inherit system;};
      pythonPackages = pkgs.python3Packages;
    in {
      devShells.default = pkgs.mkShell {
        name = "python-venv";
        venvDir = "./.venv";
        buildInputs = with pkgs; [
          # A Python interpreter including the 'venv' module is required to bootstrap
          # the environment.
          pythonPackages.python

          # This executes some shell code to initialize a venv in $venvDir before
          # dropping into the shell
          pythonPackages.venvShellHook

          qrencode
          httpie
          # echo "D$(http post "https://7245d903793b99.lhr.life/swish/dummy/" -b | tr -d '\"')" | qrencode -- -t ANSI
          # http post https://mpc.getswish.net/qrg-swish/api/v1/commerce format=png size=300 token="$(http post "https://5567ed24bbd129.lhr.life/swish/dummy/" | tr -d '\"')" -d
        ];

        # Run this command, only after creating the virtual environment
        postVenvCreation = ''
          unset SOURCE_DATE_EPOCH
          pip install -r requirements.txt
        '';

        # Now we can execute any commands within the virtual environment.
        # This is optional and can be left out to run pip manually.
        postShellHook = ''
          # allow pip to install wheels
          unset SOURCE_DATE_EPOCH
        '';
      };
    });
}
