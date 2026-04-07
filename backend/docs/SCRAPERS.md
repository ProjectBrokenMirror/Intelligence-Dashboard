# Adding a site scraper

1. **Prefer RSS** — If the outlet publishes a feed, add it to [`config/sources.yaml`](../config/sources.yaml) with `kind: rss` and `feed_url`. No code changes.

2. **New scraper module** — Copy [`app/scrapers/stub.py`](../app/scrapers/stub.py) to a new file under `app/scrapers/`, e.g. `mipaper.py`. Implement `fetch()` to return a list of `NormalizedItem` (`title`, `url`, optional `summary`, `published_at`).

3. **Register** — Import your class in [`app/scrapers/__init__.py`](../app/scrapers/__init__.py) and add it to `SCRAPER_REGISTRY` with a short key, e.g. `mipaper: MiPaperScraper`.

4. **Configure** — Add a source entry in `sources.yaml`:

   ```yaml
   - id: mi-paper
     name: Mi Periódico
     kind: scraper
     scraper_module: mipaper
     enabled: true
   ```

5. **Operations** — Honor `robots.txt`, use modest concurrency, and log failures. Scrapers break when HTML changes; treat alerts on empty results or ingest errors as a signal to update selectors.

6. **Trigger ingest** — `POST /ingest/run` or wait for the scheduled job. Check `GET /status` for counts and last fetch time.
