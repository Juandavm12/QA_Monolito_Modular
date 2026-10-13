"""Generate local, reproducible API evidence from an isolated SQLite database."""

from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

from fastapi.testclient import TestClient

from app.main import create_app
from scripts.seed_data import seed_synthetic_data

EVIDENCE_DIRECTORY = Path("evidencias") / "api"


def write_response(name: str, response: Any, expected_status: int) -> None:
    """Validate and save one HTTP response as formatted UTF-8 JSON.

    Args:
        name: Stable filename stem for the captured response.
        response: HTTP response returned by FastAPI's TestClient.
        expected_status: Expected HTTP status code for the request.

    Raises:
        RuntimeError: If the actual HTTP status differs from the expected one.
    """
    if response.status_code != expected_status:
        raise RuntimeError(
            f"{name}: expected HTTP {expected_status}, got {response.status_code}."
        )

    output_path = EVIDENCE_DIRECTORY / f"{name}.json"
    output_path.write_text(
        json.dumps(response.json(), ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def main() -> None:
    """Capture the documented HTTP sequence using a disposable seeded database."""
    EVIDENCE_DIRECTORY.mkdir(parents=True, exist_ok=True)

    with TemporaryDirectory(prefix="lab04-api-evidence-") as temporary_directory:
        database_path = Path(temporary_directory) / "api-evidence.db"
        application = create_app(f"sqlite:///{database_path}")
        database = application.state.database
        seed_synthetic_data(database)

        try:
            with TestClient(application) as client:
                write_response("salud", client.get("/health"), 200)
                write_response("productos", client.get("/products"), 200)
                write_response(
                    "inventario-antes",
                    client.get("/inventory/product-active"),
                    200,
                )
                order_response = client.post(
                    "/orders",
                    json={"product_id": "product-active", "quantity": 3},
                )
                write_response("pedido-exitoso", order_response, 201)
                retrieved = client.get(f"/orders/{order_response.json()['id']}")
                write_response("pedido-consultado", retrieved, 200)
                if retrieved.json() != order_response.json():
                    raise RuntimeError("Retrieved order differs from created order.")
                write_response(
                    "inventario-despues",
                    client.get("/inventory/product-active"),
                    200,
                )
                write_response(
                    "stock-insuficiente",
                    client.post(
                        "/orders",
                        json={"product_id": "product-active", "quantity": 8},
                    ),
                    409,
                )
                write_response(
                    "cantidad-invalida",
                    client.post(
                        "/orders",
                        json={"product_id": "product-active", "quantity": 0},
                    ),
                    422,
                )
                write_response(
                    "producto-inactivo",
                    client.post(
                        "/orders",
                        json={"product_id": "product-inactive", "quantity": 2},
                    ),
                    409,
                )
        finally:
            database.engine.dispose()

    print("API evidence: complete")


if __name__ == "__main__":
    main()
