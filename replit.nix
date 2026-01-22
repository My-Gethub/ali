{ pkgs }: {
  deps = [
    pkgs.python311
    pkgs.python311Packages.pip
    pkgs.postgresql
    pkgs.stdenv.cc.cc.lib
    pkgs.libffi
    pkgs.openssl
  ];
}
