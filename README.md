# har-endpoint-finder

A site renders fine in the browser but the HTML is empty - the data is coming
from some XHR/fetch call in the background. This finds those calls.

Open DevTools → Network, reload the page, right-click → "Save all as HAR", then:

```
python harfind.py page.har
```

It scores every request in the HAR and prints the ones that actually carry data,
best first - ignoring the HTML, CSS, images, fonts and trackers.

```
2 candidate endpoint(s), best first:

[14] GET  https://shop.example.com/api/v2/products?page=1&sort=price
     json response, api-ish path, has query params, returns a list of 3, 9kb body

[13] POST https://shop.example.com/graphql
     json response, api-ish path, post, json object, 1 keys, 5kb body
```

## How it scores

Each request gets points for looking like a data endpoint and loses if it's an
asset. Roughly: JSON response (+5), api-ish path like `/api` `/graphql` (+3),
body that parses to a list (+4) or a keyed object (+3), query params, non-GET
method, large body. Anything ending in `.css/.png/.js/...` is dropped.

Nothing here is tuned to a specific site - point it at any HAR.

## Run the sample

```
python harfind.py sample.har
python test_harfind.py
```

No dependencies, standard library only. `python >= 3.8`.
