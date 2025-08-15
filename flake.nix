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
          (pkgs.python312.withPackages (ps: [
            ps.numpy
            ps.pandas
            ps.streamlit
            ps.openpyxl
          ]))
          pkgs.git
        ];

        shellHook = ''
          echo "🐍 $(python --version)"
          echo "💡 Streamlit: streamlit run app.py"
        '';
      };
    });
}
