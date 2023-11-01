from pathlib import Path

homefilepath = Path.home()
filepath = homefilepath.joinpath(".config/ddns")
filepath.mkdir(parents=True, exist_ok=True)

database_path = filepath.joinpath("ddns.db")
logfile = filepath.joinpath("ddns.log")
