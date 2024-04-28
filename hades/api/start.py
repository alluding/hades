from __future__ import annotations
from typing import (
    Dict,
    Optional,
    Dict,
    List,
    TypeVar,
    TypedDict
)

from flask import (
    Flask,
    request,
    Response,
    render_template
)

from pydantic import BaseModel
from enum import Enum

import json
import os

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["JSONIFY_PRETTYPRINT_REGULAR"] = True


class EmbedPayload(BaseModel):
    redirect: Optional[str] = None
    title: str
    url: str = "https://discord.com/"
    color: Optional[str] = None
    image: Optional[str] = None
    thumbnail: Optional[str] = None
    description: str


class Database(TypedDict):
    embeds: Dict[str, List[str]]


class EmbedStatus(Enum):
    EMBED_NOT_FOUND = "Embed not found"


db: Database[EmbedPayload] = Database(
    json.load(open("./hades/api/database.json", "r")))


@app.route("/create", methods=["POST"])
def create_embed():
    _id = os.urandom(5).hex()

    payload = EmbedPayload(**request.json)
    db["embeds"][_id] = payload.__dict__
    with open("./hades/api/database.json", "w") as f:
        json.dump(db, f)
    return {"id": _id}


@app.route("/<_id>")
def fetch_embed(_id: str):
    embed = db["embeds"].get(_id)
    if embed:
        embed = EmbedPayload(**embed)
        embed.thumbnail = bool(embed.thumbnail)
        return render_template("template.html", **embed.dict())
    else:
        return Response(response=json.dumps({"message": "Embed not found"}), status=404)


if __name__ == "__main__":
    app.run(
        port=5000,
        host="0.0.0.0",
        debug=True
    )
