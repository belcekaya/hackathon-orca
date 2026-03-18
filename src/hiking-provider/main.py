import logging
import json
import uuid
from datetime import datetime
from openai import OpenAI
from orca import create_agent_app, ChatMessage, OrcaHandler, Variables

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Official Ibiza walking routes — sourced from ibiza.travel walking guide
# Routes 4 and 9 are temporarily unavailable
# ---------------------------------------------------------------------------
ROUTES = {
    "route-1": {
        "id": "route-1", "number": 1,
        "name": "Ibiza – Cap Martinet – S'Estanyol",
        "level": "low", "distance_km": 13.3,
        "duration_hours": 2.75, "duration_label": "2.5–3 hours",
        "altitude_m": 110, "start_point": "Ibiza harbour",
        "min_age": 0, "pushchair_friendly": True, "family_friendly": True,
        "highlights": ["Dalt Vila UNESCO views", "Ses Feixes wetlands", "S'Estanyol beach"],
        "description": "Gentle coastal walk from Ibiza harbour past UNESCO-listed Dalt Vila to S'Estanyol beach. Flat promenade sections — the only route fully suitable for pushchairs.",
        "notes": "Suitable for all walkers including pushchairs.",
    },
    "route-2": {
        "id": "route-2", "number": 2,
        "name": "Cala Llonga – Cap des Llibrell – Sol d'en Serra",
        "level": "low", "distance_km": 4.7,
        "duration_hours": 2.0, "duration_label": "2 hours",
        "altitude_m": 215, "start_point": "Cala Llonga beach",
        "min_age": 10, "pushchair_friendly": False, "family_friendly": False,
        "highlights": ["Ancient Phoenician settlement", "220m panoramic viewpoint", "Tagomago island views"],
        "description": "Short but steep route to the Phoenician settlement at Cap des Llibrell. Deceptively challenging — 215m gain in 4.7km. Experienced walkers only.",
        "notes": "Only suitable for those used to walking. No pushchairs.",
    },
    "route-3": {
        "id": "route-3", "number": 3,
        "name": "Portinatx – Faro de Moscarter",
        "level": "low", "distance_km": 12.5,
        "duration_hours": 2.75, "duration_label": "2.5–3 hours",
        "altitude_m": 65, "start_point": "Es Portitxol beach, Portinatx",
        "min_age": 6, "pushchair_friendly": False, "family_friendly": True,
        "highlights": ["Moscarter lighthouse", "Rocky coastal coves", "Views of Ses Formigues"],
        "description": "Beautiful low-level coastal walk from Portinatx to the Moscarter lighthouse. Mostly flat with some rocky sections — great for kids 6+.",
        "notes": "Suitable for almost all walkers. No pushchairs.",
    },
    "route-5": {
        "id": "route-5", "number": 5,
        "name": "Sant Antoni – Cala Salada",
        "level": "medium", "distance_km": 12.3,
        "duration_hours": 3.25, "duration_label": "3–3.5 hours",
        "altitude_m": 77, "start_point": "Sant Antoni Town Hall",
        "min_age": 7, "pushchair_friendly": False, "family_friendly": True,
        "highlights": ["Sant Antoni harbour", "Sa Conillera island views", "Cala Salada beach"],
        "description": "Scenic coastal walk from Sant Antoni along the rugged west coast to Cala Salada beach. Long but gentle — good for kids 7+.",
        "notes": "Suitable for almost all walkers. No pushchairs.",
    },
    "route-6": {
        "id": "route-6", "number": 6,
        "name": "Sant Mateu – Torres d'en Lluc",
        "level": "medium", "distance_km": 11.3,
        "duration_hours": 3.75, "duration_label": "3.5–4 hours",
        "altitude_m": 264, "start_point": "Sant Mateu d'Albarca church",
        "min_age": 8, "pushchair_friendly": False, "family_friendly": True,
        "highlights": ["Traditional Ibicenco farmhouses", "Torres d'en Lluc cliff towers", "Cala d'Albarca views"],
        "description": "Rewarding inland and coastal walk through traditional farmland to cliff-top towers. 264m gain — best for kids 8+.",
        "notes": "Suitable for almost all walkers. No pushchairs.",
    },
    "route-7": {
        "id": "route-7", "number": 7,
        "name": "Sant Josep – Sa Talaia",
        "level": "high", "distance_km": 14.0,
        "duration_hours": 4.75, "duration_label": "4.5–5 hours",
        "altitude_m": 354, "start_point": "Sant Josep de Sa Talaia church",
        "min_age": 12, "pushchair_friendly": False, "family_friendly": False,
        "highlights": ["Sa Talaia — Ibiza's highest peak at 475m", "Panoramic view of entire island"],
        "description": "The ultimate Ibiza hike — challenging ascent to Sa Talaia at 475m with views of the entire island. Too demanding for young children.",
        "notes": "May be tiring for children. No pushchairs.",
    },
    "route-8": {
        "id": "route-8", "number": 8,
        "name": "Sant Joan – Morna – Forn des Saig",
        "level": "high", "distance_km": 14.4,
        "duration_hours": 4.75, "duration_label": "4.5–5 hours",
        "altitude_m": 289, "start_point": "Sant Joan de Labritja church",
        "min_age": 7, "pushchair_friendly": True, "family_friendly": True,
        "highlights": ["Ancient olive trees", "Forn des Saig tar oven", "Morna valley", "Tagomago views"],
        "description": "Long circular route through scenic Morna valley with historical sites. Fit kids 7–8+ who are used to walking can manage this. All-terrain pushchair possible.",
        "notes": "Fine for children 7–8 used to walking. All-terrain pushchairs possible.",
    },
}

BOOKINGS = {}

SYSTEM_PROMPT = """You are the Ibiza Hiking Trails provider agent. You manage official walking routes
across Ibiza sourced from the ibiza.travel guide. Routes 4 and 9 are currently unavailable.

You help users and other AI agents find and book hiking routes. Be concise and data-rich.

Family suitability quick guide:
- Route 1: All ages, pushchair-friendly. Only flat route.
- Route 3: Ages 6+
- Route 5: Ages 7+
- Route 8: Ages 7–8+ (fit, used to walking), all-terrain pushchair OK
- Route 6: Ages 8+
- Route 2: Ages 10+ only (steep despite LOW rating)
- Route 7: Ages 12+ (challenging)

When another agent asks you a question, respond with structured, actionable data."""

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_routes",
            "description": "Search and filter hiking routes by difficulty, age, duration or family-friendliness",
            "parameters": {
                "type": "object",
                "properties": {
                    "level": {"type": "string", "enum": ["low", "medium", "high", "any"], "default": "any"},
                    "family_friendly": {"type": "boolean"},
                    "max_min_age": {"type": "integer", "description": "Return routes where min_age <= this value"},
                    "max_duration_hours": {"type": "number"},
                    "pushchair_friendly": {"type": "boolean"},
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_route_details",
            "description": "Get full details of a specific route by ID",
            "parameters": {
                "type": "object",
                "properties": {
                    "route_id": {"type": "string", "description": "e.g. route-1, route-3"},
                },
                "required": ["route_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "book_route",
            "description": "Book a hiking route for a group",
            "parameters": {
                "type": "object",
                "properties": {
                    "route_id": {"type": "string"},
                    "date": {"type": "string", "description": "YYYY-MM-DD"},
                    "group_size": {"type": "integer"},
                    "contact_name": {"type": "string"},
                    "notes": {"type": "string", "description": "Special requirements e.g. children ages"},
                },
                "required": ["route_id", "date", "group_size", "contact_name"],
            },
        },
    },
]


def _search_routes(level="any", family_friendly=None, max_min_age=None,
                   max_duration_hours=None, pushchair_friendly=None):
    results = []
    for r in ROUTES.values():
        if level != "any" and r["level"] != level:
            continue
        if family_friendly is not None and r["family_friendly"] != family_friendly:
            continue
        if max_min_age is not None and r["min_age"] > max_min_age:
            continue
        if max_duration_hours is not None and r["duration_hours"] > max_duration_hours:
            continue
        if pushchair_friendly is not None and r["pushchair_friendly"] != pushchair_friendly:
            continue
        results.append(r)
    return sorted(results, key=lambda x: x["number"])


def _book_route(route_id, date, group_size, contact_name, notes=None):
    if route_id not in ROUTES:
        return {"success": False, "reason": f"Route '{route_id}' not found"}
    try:
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        return {"success": False, "reason": "Invalid date format, use YYYY-MM-DD"}
    route = ROUTES[route_id]
    ref = f"IBZ-{uuid.uuid4().hex[:6].upper()}"
    booking = {
        "booking_ref": ref,
        "route_id": route_id,
        "route_name": route["name"],
        "date": date,
        "group_size": group_size,
        "contact_name": contact_name,
        "notes": notes or "",
        "start_point": route["start_point"],
        "level": route["level"],
        "duration_label": route["duration_label"],
        "status": "confirmed",
    }
    BOOKINGS[ref] = booking
    return {"success": True, "booking": booking}


def _execute_tool(name, args):
    if name == "search_routes":
        routes = _search_routes(**args)
        if not routes:
            return "No routes found matching the criteria."
        lines = []
        for r in routes:
            lines.append(
                f"[{r['id']}] Route {r['number']}: {r['name']} | "
                f"Level: {r['level'].upper()} | {r['distance_km']}km | {r['duration_label']} | "
                f"Min age: {r['min_age']} | Pushchair: {'yes' if r['pushchair_friendly'] else 'no'} | "
                f"{r['description']}"
            )
        return "\n".join(lines)

    elif name == "get_route_details":
        r = ROUTES.get(args["route_id"])
        if not r:
            return f"Route '{args['route_id']}' not found."
        return (
            f"Route {r['number']}: {r['name']}\n"
            f"Level: {r['level'].upper()} | {r['distance_km']}km | {r['duration_label']} | "
            f"{r['altitude_m']}m altitude\n"
            f"Start: {r['start_point']}\n"
            f"Min age: {r['min_age']} | Pushchair: {'yes' if r['pushchair_friendly'] else 'no'}\n"
            f"Highlights: {', '.join(r['highlights'])}\n"
            f"{r['description']}\n"
            f"Notes: {r['notes']}"
        )

    elif name == "book_route":
        res = _book_route(**args)
        if res["success"]:
            b = res["booking"]
            return (
                f"BOOKING CONFIRMED\n"
                f"Reference: {b['booking_ref']}\n"
                f"Route: {b['route_name']}\n"
                f"Date: {b['date']} | Group: {b['group_size']} people\n"
                f"Start point: {b['start_point']}\n"
                f"Duration: {b['duration_label']} | Level: {b['level'].upper()}\n"
                f"Notes: {b['notes'] or '—'}"
            )
        return f"Booking failed: {res['reason']}"

    return f"Unknown tool: {name}"


async def process_message(data: ChatMessage):
    handler = OrcaHandler()
    session = handler.begin(data)

    try:
        variables = Variables(data.variables)
        openai_key = variables.get("OPENAI_API_KEY")
        if not openai_key:
            session.stream("Missing OPENAI_API_KEY — please set it in the agent variables.")
            session.close()
            return

        client = OpenAI(api_key=openai_key)
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": data.message},
        ]

        # Agentic loop — runs until no more tool calls
        while True:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                tools=TOOLS,
                tool_choice="auto",
            )
            msg = response.choices[0].message

            if not msg.tool_calls:
                session.stream(msg.content or "")
                break

            messages.append({"role": "assistant", "tool_calls": [
                {"id": tc.id, "type": "function",
                 "function": {"name": tc.function.name, "arguments": tc.function.arguments}}
                for tc in msg.tool_calls
            ]})

            for tc in msg.tool_calls:
                args = json.loads(tc.function.arguments)
                result = _execute_tool(tc.function.name, args)
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": result,
                })

        session.close()

    except Exception as e:
        logger.exception("Error processing message")
        session.error("Something went wrong.", exception=e)


app, orca = create_agent_app(
    process_message_func=process_message,
    title="Ibiza Hiking Trails",
    description="Official Ibiza walking routes — search, recommend and book guided hikes across the island.",
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
