import pytest
from backend.ai.intent import classify_intent
from backend.ai.chatbot import process_chat_message
from backend.ai.language import SUPPORTED_LANGUAGES, get_template


def test_classify_intent_route():
    intent = classify_intent("Find best route from Guwahati to Imphal for vegetables")
    assert intent.name == "route_planning"
    assert intent.parameters.get("origin") == "Guwahati"
    assert intent.parameters.get("destination") == "Imphal"


def test_classify_intent_weather():
    intent = classify_intent("What is the weather like in Shillong?")
    assert intent.name == "weather_query"


def test_classify_intent_incident():
    intent = classify_intent("Show active landslide alerts and incidents")
    assert intent.name == "incident_query"


def test_chatbot_process_message_en():
    res = process_chat_message("Plan route from Guwahati to Imphal", lang="en")
    assert res["reply"] is not None
    assert len(res["reply"]) > 0
    assert res["action"] == "SHOW_ROUTE"
    assert res["data"] is not None


def test_chatbot_multilingual_hi():
    res = process_chat_message("Guwahati se Imphal route", lang="hi")
    assert res["reply"] is not None
    assert "मार्ग" in res["reply"] or "दूरी" in res["reply"] or "सिफारिश" in res["reply"]


def test_chatbot_multilingual_ta():
    res = process_chat_message("Guwahati to Imphal route", lang="ta")
    assert res["reply"] is not None
    assert "வழித்தடம்" in res["reply"] or "தூரம்" in res["reply"]
