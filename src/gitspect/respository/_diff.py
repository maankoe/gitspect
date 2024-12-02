def parse_diff(diff):
    for line in diff.splitlines():
        if line.startswith("diff --git"):
            pass
        elif line.startswith("---"):
            pass
        elif line.startswith("+++"):
            pass
        elif line.startswith("@@"):
            pass
        elif line.startswith("index"):
            pass
