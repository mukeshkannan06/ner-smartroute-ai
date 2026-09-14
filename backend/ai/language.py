"""
Language Support
------------------
Translation templates and language utilities for the chatbot.
"""
from typing import Dict, Any

# Supported languages with metadata
SUPPORTED_LANGUAGES = {
    "en": {"name": "English", "native": "English", "flag": "🇬🇧", "status": "full", "speech_code": "en-IN"},
    "ta": {"name": "Tamil", "native": "தமிழ்", "flag": "🇮🇳", "status": "full", "speech_code": "ta-IN"},
    "hi": {"name": "Hindi", "native": "हिन्दी", "flag": "🇮🇳", "status": "full", "speech_code": "hi-IN"},
    "as": {"name": "Assamese", "native": "অসমীয়া", "flag": "🌄", "status": "experimental", "speech_code": "as-IN"},
    "mni": {"name": "Manipuri", "native": "মেইতেই", "flag": "🌄", "status": "experimental", "speech_code": "mni-IN"},
    "brx": {"name": "Bodo", "native": "Bodo", "flag": "🌄", "status": "experimental", "speech_code": "brx-IN"},
    "kha": {"name": "Khasi", "native": "Khasi", "flag": "🌄", "status": "experimental", "speech_code": "en-IN"},
    "lus": {"name": "Mizo", "native": "Mizo", "flag": "🌄", "status": "experimental", "speech_code": "en-IN"},
    "kok": {"name": "Kokborok", "native": "Kokborok", "flag": "🌄", "status": "experimental", "speech_code": "en-IN"},
}

# Response templates for each language
TEMPLATES = {
    "en": {
        "route_intro": "Based on the current route and risk analysis, I recommend:",
        "route_path": "Route: {path}",
        "distance": "Distance: {distance} km",
        "eta": "ETA: {eta} hours",
        "risk": "Risk: {risk}% ({risk_level})",
        "accessibility": "Accessibility: {accessibility}/100",
        "cost": "Estimated Cost: ₹{cost}",
        "alternative_note": "The alternative route has a higher {factor}-related disruption risk.",
        "no_route": "No route found between these locations. Some roads may be closed.",
        "weather_intro": "Current weather conditions for {location}:",
        "incidents_intro": "Active incidents in the NER road network:",
        "no_incidents": "No active incidents reported in this area.",
        "closure_intro": "Road closure simulation results:",
        "ai_unavailable": "AI conversational service unavailable. SmartRoute calculation remains available.",
        "welcome": "Hello! I'm NER SmartRoute AI. I can help you plan routes, check weather, assess risks, and simulate road closures across North-East India. How can I help you?",
        "help": "I can help with:\n• Route planning between NER cities\n• Weather conditions\n• Road risk assessment\n• Incident alerts\n• Road closure simulation\n• Logistics cost estimation\n\nTry: 'Find the safest route from Guwahati to Imphal'",
    },
    "hi": {
        "route_intro": "वर्तमान रूट और जोखिम विश्लेषण के आधार पर, मेरी सिफारिश है:",
        "route_path": "मार्ग: {path}",
        "distance": "दूरी: {distance} किमी",
        "eta": "अनुमानित समय: {eta} घंटे",
        "risk": "जोखिम: {risk}% ({risk_level})",
        "accessibility": "पहुँच: {accessibility}/100",
        "cost": "अनुमानित लागत: ₹{cost}",
        "alternative_note": "वैकल्पिक मार्ग में {factor} से संबंधित अधिक जोखिम है।",
        "no_route": "इन स्थानों के बीच कोई मार्ग नहीं मिला। कुछ सड़कें बंद हो सकती हैं।",
        "weather_intro": "{location} के लिए वर्तमान मौसम:",
        "incidents_intro": "NER सड़क नेटवर्क में सक्रिय घटनाएँ:",
        "no_incidents": "इस क्षेत्र में कोई सक्रिय घटना नहीं।",
        "closure_intro": "सड़क बंद सिमुलेशन परिणाम:",
        "ai_unavailable": "AI सेवा अनुपलब्ध। SmartRoute गणना उपलब्ध है।",
        "welcome": "नमस्ते! मैं NER SmartRoute AI हूँ। मैं उत्तर-पूर्व भारत में रूट प्लानिंग, मौसम, जोखिम मूल्यांकन और सड़क बंद सिमुलेशन में मदद कर सकता हूँ। कैसे मदद करूँ?",
        "help": "मैं मदद कर सकता हूँ:\n• NER शहरों के बीच रूट प्लानिंग\n• मौसम की स्थिति\n• सड़क जोखिम मूल्यांकन\n• घटना अलर्ट\n• सड़क बंद सिमुलेशन\n• लॉजिस्टिक्स लागत अनुमान",
    },
    "ta": {
        "route_intro": "தற்போதைய வழித்தட மற்றும் ஆபத்து பகுப்பாய்வின் அடிப்படையில், நான் பரிந்துரைக்கிறேன்:",
        "route_path": "வழித்தடம்: {path}",
        "distance": "தூரம்: {distance} கிமீ",
        "eta": "மதிப்பிடப்பட்ட நேரம்: {eta} மணி நேரம்",
        "risk": "ஆபத்து: {risk}% ({risk_level})",
        "accessibility": "அணுகல்: {accessibility}/100",
        "cost": "மதிப்பிடப்பட்ட செலவு: ₹{cost}",
        "alternative_note": "மாற்று வழித்தடத்தில் {factor} தொடர்பான அதிக ஆபத்து உள்ளது.",
        "no_route": "இந்த இடங்களுக்கு இடையே வழி இல்லை.",
        "weather_intro": "{location} க்கான தற்போதைய வானிலை:",
        "incidents_intro": "NER சாலை வலையமைப்பில் செயலில் உள்ள சம்பவங்கள்:",
        "no_incidents": "இந்த பகுதியில் செயலில் உள்ள சம்பவங்கள் இல்லை.",
        "closure_intro": "சாலை மூடல் உருவகப்படுத்துதல் முடிவுகள்:",
        "ai_unavailable": "AI சேவை கிடைக்கவில்லை. SmartRoute கணக்கீடு கிடைக்கும்.",
        "welcome": "வணக்கம்! நான் NER SmartRoute AI. வடகிழக்கு இந்தியாவில் வழித்தட திட்டமிடல், வானிலை, ஆபத்து மதிப்பீடு மற்றும் சாலை மூடல் உருவகப்படுத்துதலில் உதவ முடியும்.",
        "help": "நான் உதவ முடியும்:\n• NER நகரங்களுக்கிடையே வழித்தட திட்டமிடல்\n• வானிலை நிலைமைகள்\n• சாலை ஆபத்து மதிப்பீடு\n• சம்பவ எச்சரிக்கைகள்\n• சாலை மூடல் உருவகப்படுத்துதல்",
    },
    "as": {
        "route_intro": "বৰ্তমান পথ আৰু বিপদ বিশ্লেষণৰ ওপৰত ভিত্তি কৰি, মোৰ পৰামৰ্শ:",
        "route_path": "পথ: {path}",
        "distance": "দূৰত্ব: {distance} কিঃমিঃ",
        "eta": "আনুমানিক সময়: {eta} ঘণ্টা",
        "risk": "বিপদ: {risk}% ({risk_level})",
        "accessibility": "প্ৰৱেশযোগ্যতা: {accessibility}/100",
        "cost": "আনুমানিক খৰচ: ₹{cost}",
        "alternative_note": "বিকল্প পথত {factor} সম্পৰ্কীয় অধিক বিপদ আছে।",
        "no_route": "এই স্থানসমূহৰ মাজত কোনো পথ পোৱা নগল।",
        "weather_intro": "{location} ৰ বৰ্তমান বতৰ:",
        "incidents_intro": "NER পথ নেটৱৰ্কত সক্ৰিয় ঘটনাসমূহ:",
        "no_incidents": "এই অঞ্চলত কোনো সক্ৰিয় ঘটনাৰ তথ্য নাই।",
        "closure_intro": "পথ বন্ধ অনুকৰণ ফলাফল:",
        "ai_unavailable": "AI সেৱা উপলব্ধ নহয়। SmartRoute গণনা উপলব্ধ।",
        "welcome": "নমস্কাৰ! মই NER SmartRoute AI। উত্তৰ-পূব ভাৰতত পথ পৰিকল্পনা আৰু নিৰাপদ যাত্ৰাত মই আপোনাক সহায় কৰিব পাৰোঁ।",
        "help": "মই সহায় কৰিব পাৰোঁ:\n• NER চহৰসমূহৰ মাজত পথ পৰিকল্পনা\n• বতৰৰ তথ্য\n• পথৰ বিপদ নিৰ্ণয়\n• দুৰ্ঘটনা বা পথ বন্ধৰ সতৰ্কবাৰ্তা",
    },
    "mni": {
        "route_intro": "লম্বী অমসুং খুদোংথিবা নৈনবা য়াংলগা, ঐহাক্না লমজিংবা:",
        "route_path": "লম্বী: {path}",
        "distance": "অরাপ্পা: {distance} কিঃমিঃ",
        "eta": "চংগদবা মতম: {eta} পুং",
        "risk": "খুদোংথিবা: {risk}% ({risk_level})",
        "accessibility": "চাং: {accessibility}/100",
        "cost": "অচুম্বা মমল: ₹{cost}",
        "alternative_note": "অতোপ্পা লম্বীদা {factor} খুদোংথিবা হেনগনি।",
        "no_route": "মফমশিং অসিগী মরক্তা লম্বী ফংদ্রে।",
        "weather_intro": "{location} গী নোংজু-নুংশিৎকী ফীভম:",
        "incidents_intro": "NER লম্বী নেৎৱাৰ্কতা থোক্লিবা থৌদোকশিং:",
        "no_incidents": "মফম অসিদা লম্বী থৌদোক লৈতে।",
        "closure_intro": "লম্বী থিংবগী সিমুলেসন ফল:",
        "ai_unavailable": "AI সর্বিস ফংদ্রে। SmartRoute হিসাব ফংই।",
        "welcome": "খুরুমজরি! ঐহাক NER SmartRoute AI নি। অৱাং নোংপোক ভারতকী লম্বী অমসুং সেফ রুট পানবা মতেং পাংবা ঙম্মী।",
        "help": "ঐহাক্না মতেং পাংবা ঙমগনি:\n• NER শহরশিংগী মরক্তা লম্বী পানবা\n• নোংজু-নুংশিৎ ফীভম\n• লম্বী খুদোংথিবা নৈনবা",
    },
    "brx": {
        "route_intro": "लामाया आरो खथि बिजिरनायखौ लानानै, आंनि गोसो होनाय:",
        "route_path": "लामा: {path}",
        "distance": "जान्थाय: {distance} km",
        "eta": "साननाय सम: {eta} घन्टा",
        "risk": "खथि: {risk}% ({risk_level})",
        "accessibility": "सहायनो हानाय: {accessibility}/100",
        "cost": "साननाय खरसा: ₹{cost}",
        "alternative_note": "गुबुन लामायाव {factor} खथिया बांसिन।",
        "no_route": "बे जायगानि गेजेराव जेबो लामा मोननाय जायाखै।",
        "weather_intro": "{location} नि बारहावा:",
        "incidents_intro": "NER लामायाव जाथायफोर:",
        "no_incidents": "बे ओनसोलआव जेबो जाथाय गैया।",
        "closure_intro": "लामा बन्द खालामनायनि फिथाय:",
        "ai_unavailable": "AI मदद गैया। SmartRoute थाखो दं।",
        "welcome": "खुलुमबाय! आं NER SmartRoute AI। सा-सानजा भारतनि लामा थियारि खालामनायाव मदद होनो हागौ।",
        "help": "आं मदद होनो हागौ:\n• NER सहरफोरनि लामा थियारि खालामनाय\n• बारहावा\n• लामा खथि बिजिरनाय",
    },
    "kha": {
        "route_intro": "Katkum ka jingbishar ia ka lynti bad ka jingma, nga ai jingmut:",
        "route_path": "Lynti: {path}",
        "distance": "Jingjngai: {distance} km",
        "eta": "Por ba antad: {eta} kynta",
        "risk": "Jingma: {risk}% ({risk_level})",
        "accessibility": "Ka jinglah ban rung: {accessibility}/100",
        "cost": "Dor ba antad: ₹{cost}",
        "alternative_note": "Kawei pat ka lynti ka kham don jingma na ka bynta {factor}.",
        "no_route": "Ym shem lynti hapdeng kine ki jaka.",
        "weather_intro": "Ka jinglong ka suinbneng ha {location}:",
        "incidents_intro": "Ki jingjia ha ki surok jong ka NER:",
        "no_incidents": "Ym don jingjia ba la pyntip ha kane ka jaka.",
        "closure_intro": "Ka jingpeit lypa ia ka jingkhang surok:",
        "ai_unavailable": "AI kam treikam. SmartRoute pat ka treikam.",
        "welcome": "Khublei! Nga dei ka NER SmartRoute AI. Nga lah ban iarap ban wad lynti kaba shngain ha North East.",
        "help": "Nga lah ban iarap:\n• Wad lynti hapdeng ki sor jong ka NER\n• Ka suinbneng\n• Ka jingma ha ki surok",
    },
    "lus": {
        "route_intro": "Kawng leh hlauhthawnna zirchianna aṭangin, ka rawtna chu:",
        "route_path": "Kawng: {path}",
        "distance": "Hlat zawng: {distance} km",
        "eta": "Hun mamawh chawhrual: {eta} darkar",
        "risk": "Hlauhthawnna: {risk}% ({risk_level})",
        "accessibility": "Tlawhpawh theihna: {accessibility}/100",
        "cost": "Man chawhrual: ₹{cost}",
        "alternative_note": "Kawng dang hian {factor} avangin hlauhthawnna a ngah zawk.",
        "no_route": "He hmun inkarah hian kawng hmuh a ni lo.",
        "weather_intro": "{location} khawchin dinhmun:",
        "incidents_intro": "NER kawngpui chanchin thar:",
        "no_incidents": "He laiah hian harsatna report a awm lo.",
        "closure_intro": "Kawng khar vanga nghawng zirchianna:",
        "ai_unavailable": "AI a thawk rih lo. SmartRoute a hman theih.",
        "welcome": "Chibai! NER SmartRoute AI ka ni e. North-East hmuna kawng him ber zawn kawngah ka pui thei che.",
        "help": "Ka pui thei ang che:\n• NER khawpui inkar kawng zawnna\n• Khawchin\n• Kawng him tawk loh hriatna",
    },
}


def get_template(key: str, language: str = "en") -> str:
    """Get a response template in the specified language."""
    lang_templates = TEMPLATES.get(language, TEMPLATES["en"])
    return lang_templates.get(key, TEMPLATES["en"].get(key, ""))


def format_route_response(route_data: Dict[str, Any], language: str = "en") -> str:
    """Format a route result into a human-readable response."""
    if "error" in route_data:
        return route_data["error"]

    rec = route_data.get("recommended", {})
    path = " → ".join(rec.get("path", []))
    risk_pct = round(rec.get("risk_probability", 0) * 100, 1)

    lines = [
        get_template("route_intro", language),
        "",
        get_template("route_path", language).format(path=path),
        get_template("distance", language).format(distance=rec.get("total_distance_km", "?")),
        get_template("eta", language).format(eta=rec.get("eta_hours", "?")),
        get_template("risk", language).format(risk=risk_pct, risk_level=rec.get("risk_level", "?")),
        get_template("accessibility", language).format(accessibility=rec.get("accessibility_score", "?")),
        get_template("cost", language).format(cost=f"{rec.get('estimated_cost_inr', 0):,.0f}"),
    ]

    # Add alternatives
    routes = route_data.get("routes", [])
    if len(routes) > 1:
        lines.append("")
        alt = routes[1]
        alt_path = " → ".join(alt.get("path", []))
        alt_risk = round(alt.get("risk_probability", 0) * 100, 1)
        lines.append(f"Alternative: {alt_path} ({alt.get('total_distance_km', '?')} km, "
                      f"Risk: {alt_risk}%, Accessibility: {alt.get('accessibility_score', '?')}/100)")

    return "\n".join(lines)


def format_weather_response(weather_data: Dict[str, Any], language: str = "en") -> str:
    """Format weather data into a human-readable response."""
    location = weather_data.get("location", "the area")
    lines = [
        get_template("weather_intro", language).format(location=location),
        f"🌡️ {weather_data.get('temperature_c', '?')}°C",
        f"🌧️ Rainfall: {weather_data.get('rainfall_mm', '?')} mm",
        f"💨 Wind: {weather_data.get('wind_kmph', '?')} km/h",
        f"👁️ Visibility: {weather_data.get('visibility_km', '?')} km",
        f"⚠️ Risk Level: {weather_data.get('risk_level', '?')}",
        f"Conditions: {weather_data.get('conditions', '?')}",
    ]
    return "\n".join(lines)


def format_incidents_response(incidents_data: Dict[str, Any], language: str = "en") -> str:
    """Format incidents data into a human-readable response."""
    incidents = incidents_data.get("incidents", [])
    if not incidents:
        return get_template("no_incidents", language)

    lines = [get_template("incidents_intro", language)]
    for inc in incidents:
        icon = {
            "LANDSLIDE_RISK": "⛰️", "HEAVY_RAIN": "🌧️", "TRAFFIC": "🚗",
            "FLOOD_RISK": "🌊", "POOR_VISIBILITY": "🌫️", "ROAD_CLOSURE": "🚧",
        }.get(inc.get("type", ""), "⚠️")
        lines.append(f"\n{icon} {inc.get('type', '').replace('_', ' ')} — {inc.get('road', '')}")
        lines.append(f"   Severity: {inc.get('severity', '?')}")
        lines.append(f"   {inc.get('message', '')}")

    return "\n".join(lines)
