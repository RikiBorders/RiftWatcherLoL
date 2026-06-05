from flask import Flask, request, jsonify

from ..facade.player_facade import PlayerFacade
from .rift_watcher_api import RiftWatcherAPI

app = Flask(__name__)

api = RiftWatcherAPI(PlayerFacade())


@app.route("/player/overview", methods=["GET"])
def player_overview():
    result = api.get_player_overview(
        request.args["game_name"],
        request.args["tag_line"],
        request.args["region"]
    )
    return jsonify(result)