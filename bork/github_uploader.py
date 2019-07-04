def upload(*globs):
    files = []

    for glob in globs:
        matches = map(str, Path().glob(glob))
        files += list(matches)

    print("Uploading to GitHub:")
    for filename in files:
        print("- {}".format(filename))

    raise NotImplementedError("github_uploader.upload()")

