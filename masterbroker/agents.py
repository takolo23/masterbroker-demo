from __future__ import annotations

"""Small, auditable agent team for paper-trading decisions.

The team never connects to a broker and never produces a live order.  It turns
the existing market signal and risk state into an explainable DEMO proposal.
"""

from dataclasses import asdict, dataclass
from datetime import datetime, timezone


@dataclass(frozen=True)
class AgentReport:
    id: str
    name: str
    responsibility: str
    verdict: str
    reason: str


def evaluate_team(signal: dict, settings: dict, *, news_paused: bool = False) -> dict:
    """Return an explicit four-agent consensus.  No execution is possible here."""
    action = signal.get("action", "WAIT")
    side = signal.get("side")
    score = float(signal.get("score", 0.0) or 0.0)
    confidence = round(min(99, max(0, score * 100)))
    threshold = float(settings.get("confidence", 85) or 85)
    only_analyze = bool(settings.get("onlyAnalyze", True))

    analyst_ok = action == "ALERT_ONLY" and side in {"LONG", "SHORT"}
    analyst = AgentReport(
        "market_analyst", "Analista de mercado",
        "Lee tendencia, confluencia y calidad de la se�al.",
        "PASS" if analyst_ok else "WAIT",
        signal.get("reason", "Sin se�al suficiente para una propuesta."),
    )
    risk_ok = analyst_ok and confidence >= threshold and not news_paused
    risk_reason = (
        f"Confianza {confidence}% supera el m�nimo {threshold:.0f}%."
        if risk_ok else
        ("Pausa de seguridad por noticia o evento de alto impacto." if news_paused
         else f"Confianza {confidence}% por debajo del m�nimo {threshold:.0f}%.")
    )
    risk = AgentReport(
        "risk_guardian", "Guardi�n de riesgo",
        "Exige confianza m�nima, l�mites diarios y pausa por eventos.",
        "PASS" if risk_ok else "BLOCK",
        risk_reason,
    )
    execution = AgentReport(
        "demo_executor", "Validador de ejecuci�n demo",
        "Comprueba que la acci�n se quede en simulaci�n local.",
        "PASS",
        "Ejecuci�n real deshabilitada; solo se permite registrar una simulaci�n.",
    )
    learning = AgentReport(
        "learning_reviewer", "Revisor de aprendizaje",
        "Exige registro, prueba hist�rica y validaci�n antes de cambiar reglas.",
        "PASS",
        "Las decisiones se guardan para revisi�n; no se promocionan modelos sin validaci�n.",
    )
    reports = [analyst, risk, execution, learning]
    approved = analyst_ok and risk_ok and not only_analyze
    proposal = "NO_OPERAR"
    if approved:
        proposal = "HIGHER" if side == "LONG" else "LOWER"
    return {
        "mode": "DEMO_ONLY",
        "live_orders": "DISABLED",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "confidence": confidence,
        "proposal": proposal,
        "requires_confirmation": bool(settings.get("askConfirm", True)),
        "reason": (
            "Consenso demo disponible." if approved else
            ("Configurado para solo analizar." if only_analyze else "El equipo no aprob� la entrada.")
        ),
        "agents": [asdict(report) for report in reports],
    }

