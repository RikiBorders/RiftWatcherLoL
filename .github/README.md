# RiftWatcherLoL

RiftWatcher is a production-focused League of Legends analytics platform built as a modular Flask API server. It ingests Riot match data, persists player and match state, and exposes a clean backend for analytics, coaching, and downstream integrations.

This project is designed around:
- reliable match ingestion and incremental polling
- structured player performance modeling
- API-first integration for clients such as Discord or web frontends
- extensible analytics and coaching layers

For the current roadmap, priorities, and contributor ownership opportunities, see [ROADMAP.md](./ROADMAP.md).

Design: https://docs.google.com/document/d/1yzhuZO6NVqQyVGyzCaJOYMkEXU3-a3yOHOhM5iYEpOs/edit?tab=t.0

## Quick start

You can test the API endpoints by running the invoker:

```bash
python src/rift_watcher_invoker/invoker.py
```

Run the test suite locally:

```bash
pytest
```

Build and run the app with Docker:

```bash
docker build -t riftwatcher:latest .
docker run --rm -p 5000:5000 riftwatcher:latest
```


## Contributor notes

This repository is actively evolving toward a production-quality analytics platform, and we welcome serious contributors interested in ownership of backend, data, and API slices. See [CONTRIBUTE.md](./CONTRIBUTE.md) for contribution guidelines and ownership pathways.
