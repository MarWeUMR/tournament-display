{
  description = "tournament-display";
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = {
    self,
    nixpkgs,
    flake-utils,
  }:
    flake-utils.lib.eachDefaultSystem (
      system: let
        pkgs = import nixpkgs {
          inherit system;
        };
      in {
        devShells.default = pkgs.mkShell {
          name = "tournament-display";
          nativeBuildInputs = [ ];
          buildInputs = [ ];

          packages = with pkgs; [ rye uv ];

          RYE_NO_AUTO_INSTALL="1";
        };
      }
    );
}
