{
  description = "Nix flake for working on CloudSurge's scripts";

  inputs = {
    nixpkgs.url = "nixpkgs/nixos-unstable";
  };

  outputs = {nixpkgs, ...}: let
    system = "x86_64-linux";
  in {
    devShells."${system}".default = let
      pkgs = import nixpkgs {
        inherit system;
        overlays = [
          (final: prev: {
            vhs = prev.vhs.override {
              buildGoModule = previousArgs: let
                self = prev.buildGoModule (previousArgs
                  // {
                    version = "master";
                    vendorHash = "sha256-EqxqXi5t6HToAUotzEotpFKhgrAyi+eUbk6vqHkCtJc=";
                    src = prev.fetchFromGitHub {
                      owner = "charmbracelet";
                      repo = "vhs";
                      rev = "9624cdad81eb73f050415b44bfc097fc371ba566";
                      hash = "sha256-tCNVPkdpnrrlX+4aU7GrBXSeEdgAXOXzXh6XHG9Vsao=";
                    };
                  });
              in
                self;
            };
          })
        ];
      };
    in
      pkgs.mkShell {
        packages = with pkgs; [
          vhs
          bashInteractive
        ];
      };
  };
}
