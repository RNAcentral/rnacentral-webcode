def remove_path(result, generator, request, public):
    """
    Post-processing hook to remove /api/current/ and /sequence-search/ from the schema
    """
    paths = result.get("paths", {})
    excluded_prefixes = ("/api/current/", "/sequence-search/")
    paths = {
        key: value
        for key, value in paths.items()
        if not key.startswith(excluded_prefixes)
    }
    result["paths"] = paths
    return result


def fix_path(result, generator, request, public):
    """
    Post-processing hook to normalize paths in the OpenAPI schema:
    - Fix RNA path patterns containing [_/] to only show /.
    """
    paths = result.get("paths", {})
    updated_paths = {}

    for path, details in paths.items():
        if "[/_]" in path:
            path = path.replace("[/_]", "/")

        updated_paths[path] = details

    result["paths"] = updated_paths
    return result
