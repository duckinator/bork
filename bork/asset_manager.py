from pathlib import Path
from urllib.request import urlopen


def download_assets(asset_list, directory, name_key=None, url_key=None):
    if name_key is None:
        name_key = 'name'

    if url_key is None:
        url_key = 'url'

    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)

    for asset in asset_list:
        name = asset[name_key]
        url = asset[url_key]
        path = directory / name

        contents = urlopen(url).read()

        path.write_bytes(contents)
        print(str(path))
