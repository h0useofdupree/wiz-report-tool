{
  description = "Dev shell for wiz-report-tool";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = {
    self,
    nixpkgs,
    flake-utils,
    ...
  }:
    flake-utils.lib.eachDefaultSystem (system: let
      pkgs = import nixpkgs {inherit system;};
    in {
      devShells.default = pkgs.mkShell {
        name = "wiz-report-tool-dev";

        packages = [
          pkgs.python312
          pkgs.python312Packages.venvShellHook
          pkgs.git
        ];

        venvDir = ".venv";

        # one-time setup when the venv is created
        postVenvCreation = ''
          python -m pip install --upgrade pip
          if [ -f requirements.txt ]; then
            pip install -r requirements.txt
          fi
        '';

        postShellHook = ''
          if [ -z "''${VIRTUAL_ENV-}" ]; then
            source .venv/bin/activate
          fi

          export PIP_DISABLE_PIP_VERSION_CHECK=1
          export PYTHONDONTWRITEBYTECODE=1
          echo "🐍 $(python --version)"
        '';
      };
    });
}
