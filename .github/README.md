# RiftWatcherLoL

This project is a League of Legends statistics engine built as a modular API server built with Flask, designed to provide player statistics and match data for League of Legends. It serves as a backend for a larger application that tracks and analyzes player performance in the game. The API interacts with the Riot Games API to fetch data, processes it, and returns it in a structured format for use in various client applications.

Design: https://docs.google.com/document/d/1yzhuZO6NVqQyVGyzCaJOYMkEXU3-a3yOHOhM5iYEpOs/edit?tab=t.0


You can test the API endpoints by running the invoker with `python src/rift_watcher_invoker/invoker.py`

To run basic unit tests, just run `pytest`

To build and run the app, execute the docker file:

```
docker build -t riftwatcher:latest .
docker run --rm -p 5000:5000 riftwatcher:latest
```

This project can also be deployed and managed using [homelab](https://github.com/RikiBorders/homelab)
