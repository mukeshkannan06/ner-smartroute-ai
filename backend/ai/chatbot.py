"""
NER SmartRoute AI — Conversational Chatbot Engine
-------------------------------------------------
Combines intent classification, backend tool dispatch, and multilingual
localization into a coherent chat response with actionable UI payload.
"""
from typing import Dict, Any, Optional, List
import re

from .intent import classify_intent, Intent
from . import tools, language
from ..graph_data import NODES, ROADS, all_node_names


def process_chat_message(
    message: str,
    lang: str = "en",
    context: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Process incoming user prompt or voice query.
    Returns reply text, intent, tool payload, and interactive UI action.
    """
    context = context or {}
    intent_result: Intent = classify_intent(message)
    params = intent_result.parameters
    intent_name = intent_result.name

    reply_text = ""
    action = None
    data_payload: Optional[Dict[str, Any]] = None
    structured_route: Optional[Dict[str, Any]] = None
    suggestions: List[str] = []

    # 1. Route Planning Intent
    if intent_name == "route_planning":
        origin = params.get("origin") or context.get("origin")
        destination = params.get("destination") or context.get("destination")

        if not origin or not destination:
            # Check if user mentioned just one city
            reply_text = (
                f"I noticed you want to plan a route. Please specify both origin and destination cities in NER "
                f"(e.g., 'Route from Guwahati to Imphal')."
            ) if lang == "en" else language.get_template("help", lang)
            suggestions = ["Route Guwahati to Imphal", "Safest route Dimapur to Kohima", "Fastest route Shillong to Silchar"]
        else:
            origin = origin.capitalize()
            destination = destination.capitalize()
            cargo = params.get("cargo", "General Goods")
            weight = float(params.get("weight_tonnes", 2.0))
            vehicle = params.get("vehicle_type", "truck")
            monsoon = bool(params.get("monsoon", False))

            route_result = tools.plan_route(
                origin=origin,
                destination=destination,
                vehicle_type=vehicle,
                weight_tonnes=weight,
                cargo=cargo,
                season_monsoon=monsoon,
            )

            reply_text = language.format_route_response(route_result, language=lang)
            action = "SHOW_ROUTE"
            data_payload = route_result
            structured_route = route_result.get("recommended")
            suggestions = [
                f"Check weather in {origin}",
                f"Check weather in {destination}",
                "Simulate landslide disruption",
            ]

    # 2. Weather Query Intent
    elif intent_name == "weather_query":
        location = params.get("location") or context.get("location") or "Guwahati"
        weather_data = tools.get_weather(location)
        reply_text = language.format_weather_response(weather_data, language=lang)
        action = "SHOW_WEATHER"
        data_payload = weather_data
        suggestions = ["Check active incidents", "Plan a safe route", "Network health overview"]

    # 3. Incident / Hazard Query Intent
    elif intent_name == "incident_query":
        location = params.get("location")
        incidents_data = tools.get_incidents(location)
        reply_text = language.format_incidents_response(incidents_data, language=lang)
        action = "HIGHLIGHT_INCIDENTS"
        data_payload = incidents_data
        suggestions = ["Plan safest route", "Simulate road closure", "Weather in Shillong"]

    # 4. Road Risk Assessment Intent
    elif intent_name == "risk_query":
        location = params.get("location") or "Guwahati"
        weather_data = tools.get_weather(location)
        incidents_data = tools.get_incidents(location)
        reply_text = (
            f"Risk analysis for {location}:\n"
            f"• Weather Risk: {weather_data.get('risk_level', 'Low')} ({weather_data.get('rainfall_mm', 0)} mm rain)\n"
            f"• Active Incidents: {len(incidents_data.get('incidents', []))} hazard(s) monitored.\n"
            f"All transport corridors through {location} are evaluated dynamically using Random Forest risk scoring."
        )
        action = "SHOW_RISK"
        data_payload = {"weather": weather_data, "incidents": incidents_data}
        suggestions = ["View government dashboard", "Plan alternate route", "Simulate closure"]

    # 5. Road Closure / Disruption Simulation Intent
    elif intent_name == "closure_simulation":
        road_id = params.get("road_id", "NH-001")
        reason = params.get("reason", "LANDSLIDE")
        twin_data = tools.simulate_closure(road_id=road_id)
        reply_text = (
            f"{language.get_template('closure_intro', lang)}\n"
            f"Simulated {reason} closure on {road_id} ({twin_data.get('road_closed', {}).get('a', '')} ↔ {twin_data.get('road_closed', {}).get('b', '')}).\n"
            f"• Network accessibility dropped by: {twin_data.get('accessibility_loss_pts', 0)} pts\n"
            f"• Affected active shipments: {len(twin_data.get('affected_shipments', []))}\n"
            f"• Dynamic alternate routing is active."
        )
        action = "SIMULATE_CLOSURE"
        data_payload = twin_data
        suggestions = ["Reopen all roads", "View government dashboard", "Plan safe route"]

    # 6. Accessibility Query Intent
    elif intent_name == "accessibility_query":
        access_data = tools.get_accessibility()
        reply_text = (
            f"NER Highway Network Accessibility Score: {access_data.get('network_accessibility_score', 82.5)}/100\n"
            f"• Total Roads Monitored: {access_data.get('total_roads', len(ROADS))}\n"
            f"• Critical Corridors: {len(access_data.get('critical_corridors', []))}\n"
            f"• High-Risk Routes: {len(access_data.get('high_risk_roads', []))}"
        )
        action = "SHOW_ACCESSIBILITY"
        data_payload = access_data
        suggestions = ["View critical corridors", "Check weather alerts", "Plan logistics route"]

    # 7. General Help or Default Fallback
    else:
        reply_text = language.get_template("help" if intent_name == "general_help" else "welcome", lang)
        suggestions = [
            "Route Guwahati to Imphal",
            "Weather in Shillong",
            "Show active incidents",
            "Simulate road closure on NH-001",
        ]

    return {
        "reply": reply_text,
        "intent": intent_name,
        "language": lang,
        "action": action,
        "data": data_payload,
        "structured_route": structured_route,
        "suggestions": suggestions,
    }
