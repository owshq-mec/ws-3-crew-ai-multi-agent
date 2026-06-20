"""I4 ground-truth scoring oracle for Sentinel diagnoses.

The oracle reads the ``injected_incidents`` Postgres ledger (written by the
chaos generator) and scores a crew diagnosis by exact ``failure_key`` match
against the latest injected incident.
"""

from __future__ import annotations

from src.gen.repository import session


def score_diagnosis(diagnosis_key: str) -> str:
    """Score a diagnosis against the latest incident in the I4 ledger.

    Args:
        diagnosis_key: The ``failure_key`` produced by the diagnosing crew.

    Returns:
        ``'correct'`` when ``diagnosis_key`` exactly matches the
        ``failure_key`` of the most recent row in ``injected_incidents``;
        ``'incorrect'`` otherwise (including when the ledger is empty).
    """
    conn = session()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT failure_key FROM injected_incidents "
                "ORDER BY injected_at DESC, incident_id DESC LIMIT 1"
            )
            row = cur.fetchone()
            if row is None:
                return "incorrect"
            return "correct" if row[0] == diagnosis_key else "incorrect"
    finally:
        conn.close()
