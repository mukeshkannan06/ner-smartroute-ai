"""
Intent Detection
------------------
Classifies user messages into intents and extracts parameters.
Uses pattern matching for fast, reliable detection without LLM dependency.
"""
import re
from typing import Dict, Any, Optional, List
from dataclasses import dataclass


@dataclass
class Intent:
    name: str           # route_planning, weather_query, risk_query, incident_query, closure_simulation, accessibility_query, general_help
    confidence: float   # 0-1
    parameters: Dict[str, Any]


# NER city names for extraction
NER_CITIES = [
    "guwahati", "shillong", "silchar", "dimapur", "kohima", "imphal",
    "jorhat", "aizawl", "tezpur", "nagaon", "agartala",
]

# Hindi/Tamil transliterations of city names
CITY_ALIASES = {
    "गुवाहाटी": "guwahati", "गुवाहाती": "guwahati",
    "इंफाल": "imphal", "इम्फाल": "imphal",
    "दीमापुर": "dimapur", "कोहिमा": "kohima",
    "शिलॉन्ग": "shillong", "सिल्चर": "silchar",
    "ஐசால்": "aizawl", "குவஹாத்தி": "guwahati",
    "இம்பால்": "imphal", "திமாபூர்": "dimapur",
}

# Cargo types
CARGO_TYPES = [
    "vegetables", "perishable", "fruits", "medicine", "medical",
    "construction", "fuel", "general", "fragile", "heavy", "electronics",
    "sabji", "sabzi", "dawai", "dawa",
]

VEHICLE_TYPES = ["truck", "mini_truck", "van", "car"]

# Intent patterns
ROUTE_PATTERNS = [
    r"(?:route|path|way|road|travel|go|transport|send|ship|move|deliver)\s",
    r"(?:from|se)\s+\w+\s+(?:to|tak|ko)\s+\w+",
    r"(?:best|safest|fastest|cheapest|shortest)\s+(?:route|way|path)",
    r"how\s+(?:to\s+)?(?:go|reach|get|travel)",
    r"kaise\s+(?:jaaye|pahunche|jaau)",
    r"(?:guwahati|imphal|dimapur|kohima|shillong|silchar|aizawl|tezpur|nagaon|agartala)",
]

WEATHER_PATTERNS = [
    r"weather\b", r"rain\b", r"rainfall\b", r"storm\b", r"flood\b",
    r"barish\b", r"mausam\b", r"toofan\b",
    r"மழை", r"வானிலை",
]

RISK_PATTERNS = [
    r"risk\b", r"danger\b", r"safe\b", r"unsafe\b", r"hazard\b",
    r"khatara\b", r"khatrnak\b", r"suraksha\b",
    r"ஆபத்து", r"பாதுகாப்பு",
]

INCIDENT_PATTERNS = [
    r"incident\b", r"accident\b", r"landslide\b", r"blockage\b", r"closure\b",
    r"hadsa\b", r"band\b", r"blocked\b",
]

CLOSURE_PATTERNS = [
    r"(?:close|shut|block|simulate)\s+(?:road|route|highway)",
    r"what\s+(?:if|happens)\s+(?:road|route|this)",
    r"road\s+(?:close|closed|closure|block)",
    r"agar\s+(?:road|rasta)\s+(?:band|closed)",
]

ACCESSIBILITY_PATTERNS = [
    r"accessib", r"condition\b", r"quality\b",
    r"halat\b", r"sthiti\b",
]


def detect_intent(message: str) -> Intent:
    """Detect the user's intent from their message."""
    msg_lower = message.lower().strip()


    # Extract cities from message
    cities = _extract_cities(msg_lower)
    cargo = _extract_cargo(msg_lower)
    weight = _extract_weight(msg_lower)
    vehicle = _extract_vehicle(msg_lower)

    # Score each intent
    scores = {
        "route_planning": _score_patterns(msg_lower, ROUTE_PATTERNS),
        "weather_query": _score_patterns(msg_lower, WEATHER_PATTERNS),
        "risk_query": _score_patterns(msg_lower, RISK_PATTERNS),
        "incident_query": _score_patterns(msg_lower, INCIDENT_PATTERNS),
        "closure_simulation": _score_patterns(msg_lower, CLOSURE_PATTERNS),
        "accessibility_query": _score_patterns(msg_lower, ACCESSIBILITY_PATTERNS),
    }

    # Boost route_planning if 2+ cities found (genuine origin & destination)
    if len(cities) >= 2:
        scores["route_planning"] += 0.5
    elif len(cities) == 1 and scores["weather_query"] == 0 and scores["risk_query"] == 0 and scores["incident_query"] == 0:
        scores["route_planning"] += 0.2

    # Boost weather if a city is mentioned along with weather keywords
    if scores["weather_query"] > 0 and len(cities) >= 1:
        scores["weather_query"] += 0.3

    # Boost if cargo/weight mentioned
    if cargo:
        scores["route_planning"] += 0.3
    if weight:
        scores["route_planning"] += 0.2

    # Find best intent
    best_intent = max(scores, key=scores.get)
    best_score = scores[best_intent]

    # Default to general_help if no strong match
    if best_score < 0.1:
        best_intent = "general_help"
        best_score = 0.5

    params = {}
    if cities:
        if len(cities) >= 2:
            params["origin"] = cities[0]
            params["destination"] = cities[1]
        else:
            params["location"] = cities[0]
    if cargo:
        params["cargo"] = cargo
    if weight:
        params["weight_tonnes"] = weight
    if vehicle:
        params["vehicle_type"] = vehicle

    return Intent(
        name=best_intent,
        confidence=min(best_score, 1.0),
        parameters=params,
    )


classify_intent = detect_intent



def _score_patterns(text: str, patterns: List[str]) -> float:
    """Score how many patterns match the text."""
    score = 0.0
    for pattern in patterns:
        if re.search(pattern, text, re.IGNORECASE):
            score += 0.3
    return min(score, 1.0)


_STOPWORDS_AFTER_DEST = (
    r"for|with|carrying|avoiding|during|via|using|by|in|on|"
    r"safest|fastest|cheapest|quickest|considering"
)

# Generic "from <origin> to <destination>" pattern — this is what lets the
# assistant handle ANY Indian city pair (e.g. "Chennai to Kolkata"), not just
# the 11 built-in NER demo cities.
FROM_TO_PATTERN = re.compile(
    r"from\s+([a-z][a-z .]{1,30}?)\s+to\s+([a-z][a-z .]{1,30}?)"
    r"(?:\s+(?:" + _STOPWORDS_AFTER_DEST + r")\b|[,.!?]|$)",
    re.IGNORECASE,
)
# Also accept "<origin> to <destination>" without a leading "from".
BARE_TO_PATTERN = re.compile(
    r"\b([a-z][a-z .]{1,30}?)\s+to\s+([a-z][a-z .]{1,30}?)"
    r"(?:\s+(?:" + _STOPWORDS_AFTER_DEST + r")\b|[,.!?]|$)",
    re.IGNORECASE,
)


_LEADING_STOPWORDS = {
    "route", "plan", "find", "get", "show", "calculate", "book", "give",
    "best", "safest", "fastest", "cheapest", "quickest", "shortest",
    "way", "path", "road", "the", "a", "an", "me", "please", "need",
    "want", "us", "our", "my", "i", "trip", "journey", "travel",
}


def _title_case_city(raw: str) -> str:
    """Title-case a captured place name, stripping leading command words
    (e.g. "Route Guwahati" -> "Guwahati") that a greedy regex may have
    swept up along with the actual place name."""
    words = raw.strip().split()
    while words and words[0].lower() in _LEADING_STOPWORDS:
        words.pop(0)
    return " ".join(w.capitalize() for w in words)


def _extract_cities(text: str) -> List[str]:
    """
    Extract origin/destination city names from text.

    Tries a generic "from X to Y" / "X to Y" pattern first so any Indian
    city pair can be recognized, then falls back to the built-in NER city
    list and known transliterated aliases (used for weather/risk/incident
    single-location queries).
    """
    for pattern in (FROM_TO_PATTERN, BARE_TO_PATTERN):
        match = pattern.search(text)
        if match:
            origin_raw, dest_raw = match.group(1), match.group(2)
            origin = _title_case_city(origin_raw)
            dest = _title_case_city(dest_raw)
            if origin and dest and origin.lower() != dest.lower():
                return [origin, dest]

    found = []

    # Check aliases first
    for alias, city in CITY_ALIASES.items():
        if alias in text:
            canonical = city.capitalize()
            if canonical not in found:
                found.append(canonical)

    # Check direct city names (NER demo network)
    for city in NER_CITIES:
        if city in text:
            canonical = city.capitalize()
            if canonical not in found:
                found.append(canonical)

    return found


def _extract_cargo(text: str) -> Optional[str]:
    """Extract cargo type from text."""
    for cargo in CARGO_TYPES:
        if cargo in text:
            return cargo.capitalize()
    return None


def _extract_weight(text: str) -> Optional[float]:
    """Extract weight in tonnes from text."""
    patterns = [
        r"(\d+(?:\.\d+)?)\s*(?:tonne|ton|t\b)",
        r"(\d+(?:\.\d+)?)\s*(?:kg|kilogram)",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            val = float(match.group(1))
            if "kg" in text.lower():
                val = val / 1000
            return val
    return None


def _extract_vehicle(text: str) -> Optional[str]:
    """Extract vehicle type from text."""
    for v in VEHICLE_TYPES:
        if v.replace("_", " ") in text or v in text:
            return v
    return None
