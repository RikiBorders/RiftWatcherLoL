from flask import Flask, request, jsonify
import os
import logging


def create_app():
    """Application factory that initializes dependencies at process startup.

    This keeps top-level imports light while still constructing clients
    once when the WSGI server calls the factory.
    """
    app = Flask(__name__)
    logger = logging.getLogger(__name__)

    # Build dependencies (run at startup)
    api = None
    try:
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

        db_client = None
        if supabase_url and supabase_key:
            try:
                from ..client.database_client import DatabaseClient

                db_client = DatabaseClient(supabase_url=supabase_url, supabase_key=supabase_key)
            except Exception:
                logger.exception("Failed to initialize DatabaseClient at startup")
                db_client = None
        else:
            logger.info("SUPABASE vars not provided; DatabaseClient not initialized")

        from ..client.riot_api_client import RiotAPIClient
        from ..adapter.riot_adapter import RiotAdapter
        from ..utils.stat_calculator import StatCalculator
        from ..facade.player_facade import PlayerFacade
        from .rift_watcher_api import RiftWatcherAPI

        default_region = os.getenv("RIOT_DEFAULT_REGION", "NA")
        riot_client = RiotAPIClient(region=default_region, database_client=db_client)

        adapter = RiotAdapter(db_client, riot_client)
        stat_calc = StatCalculator(db_client, adapter)
        facade = PlayerFacade(adapter, stat_calc)
        api = RiftWatcherAPI(facade)

    except Exception:
        logger.exception("Failed to initialize app dependencies at startup")
        api = None

    app.config["API"] = api

    @app.route("/player/overview", methods=["GET"])
    def player_overview():
        api = app.config.get("API")
        if api is None:
            return jsonify({"error": "service unavailable"}), 503

        result = api.get_player_overview(
            request.args["game_name"],
            request.args["tag_line"],
            request.args["region"],
        )
        return jsonify(result)

    return app


# For simple dev usage (e.g., `flask run`), expose an `app` variable.
app = create_app()