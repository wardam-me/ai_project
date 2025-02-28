
{pkgs}: {
  deps = [
    pkgs.sqlite
    pkgs.tk
    pkgs.tcl
    pkgs.qhull
    pkgs.pkg-config
    pkgs.gtk3
    pkgs.gobject-introspection
    pkgs.ghostscript
    pkgs.freetype
    pkgs.ffmpeg-full
    pkgs.cairo
    pkgs.postgresql
    pkgs.openssl
    pkgs.python311
    pkgs.python311Packages.pip
    pkgs.python311Packages.flask
    pkgs.python311Packages.flask-sqlalchemy
    pkgs.python311Packages.flask-login
    pkgs.python311Packages.matplotlib
    pkgs.python311Packages.numpy
    pkgs.python311Packages.psutil
    pkgs.python311Packages.gunicorn
    pkgs.python311Packages.python-dotenv
    pkgs.python311Packages.werkzeug
  ];
}
