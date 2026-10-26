import harfind


def test_finds_the_data_endpoints():
    hits = harfind.find("sample.har")
    urls = [h[2] for h in hits]
    assert any("/api/v2/products" in u for u in urls)
    assert any("/graphql" in u for u in urls)
    # the api call returning a list should outrank the graphql one
    assert "/api/v2/products" in hits[0][2]


def test_ignores_static_and_trackers():
    hits = harfind.find("sample.har")
    urls = [h[2] for h in hits]
    assert not any(u.endswith(".css") or u.endswith(".png") for u in urls)
    assert not any("track" in u for u in urls)


if __name__ == "__main__":
    test_finds_the_data_endpoints()
    test_ignores_static_and_trackers()
    print("ok")
