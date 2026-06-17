def remove_register_endpoint(endpoints):
    filtered = []

    for path, path_regex, method, callback in endpoints:
        if path == "/api/register/":
            continue

        filtered.append((path, path_regex, method, callback))

    return filtered