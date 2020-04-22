import sys
from pathlib import Path

if sys.platform == "win32":
    try:
        from win32com.shell import shell, shellcon

        def get_home_dir():
            return Path(shell.SHGetSpecialFolderPath(0, shellcon.CSIDL_PROFILE))

        def get_appstate_dir():
            return Path(shell.SHGetSpecialFolderPath(0, shellcon.CSIDL_APPDATA))

    except ImportError:
        def get_home_dir():
            return Path().home()

        def get_appstate_dir():
            homedir = get_home_dir()
            winversion = sys.getwindowsversion()
            if winversion[0] == 6:
                appdir = homedir / "AppData" / "Roaming"
            else:
                appdir = homedir / "Application Data"
            return appdir
else:
    # linux or darwin (mac)
    def get_home_dir():
        return Path().home()

    def get_appstate_dir():
        return get_home_dir() / ".Tribler"
