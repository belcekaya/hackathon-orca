import logging
import httpx
from typing import Optional
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools import tool
from orca import create_agent_app, ChatMessage, OrcaHandler, Variables

logger = logging.getLogger(__name__)

# API Configuration
API_BASE_URL = "https://hacketon-18march-api.orcaplatform.ai/car-rental-1/api"
API_KEY = "car-rental-1-key-stu901"


def get_headers():
    return {"X-API-Key": API_KEY}


# === Car Rental API Tools ===

@tool
def get_categories() -> str:
    """Get all vehicle categories with their daily rate ranges.
    Use this to show customers what types of vehicles are available and their price ranges.
    """
    with httpx.Client() as client:
        response = client.get(f"{API_BASE_URL}/categories", headers=get_headers())
        if response.status_code == 200:
            categories = response.json()
            result = "Vehicle Categories:\n"
            for cat in categories:
                result += f"- {cat['category']}: ${cat['min_daily_rate']}-${cat['max_daily_rate']}/day ({cat['vehicle_count']} vehicles)\n"
            return result
        return f"Error: {response.status_code} - {response.text}"


@tool
def get_vehicles(category: Optional[str] = None, min_seats: Optional[int] = None) -> str:
    """List all vehicles in the fleet.

    Args:
        category: Filter by category (economy, compact, midsize, fullsize, suv, premium, luxury)
        min_seats: Filter by minimum number of seats
    """
    params = {}
    if category:
        params["category"] = category
    if min_seats:
        params["seats"] = min_seats

    with httpx.Client() as client:
        response = client.get(f"{API_BASE_URL}/vehicles", headers=get_headers(), params=params)
        if response.status_code == 200:
            vehicles = response.json()
            if not vehicles:
                return "No vehicles found matching your criteria."
            result = f"Found {len(vehicles)} vehicle(s):\n"
            for v in vehicles:
                result += f"- ID {v['id']}: {v['year']} {v['make']} {v['model']} ({v['category']}) - {v['seats']} seats - ${v['daily_rate']}/day - {v['status']}\n"
            return result
        return f"Error: {response.status_code} - {response.text}"


@tool
def check_availability(pickup_date: str, return_date: str, category: Optional[str] = None, min_seats: Optional[int] = None) -> str:
    """Find vehicles available for a specific date range.

    Args:
        pickup_date: Pickup date in YYYY-MM-DD format
        return_date: Return date in YYYY-MM-DD format
        category: Filter by category (economy, compact, midsize, fullsize, suv, premium, luxury)
        min_seats: Filter by minimum number of seats
    """
    params = {"pickup_date": pickup_date, "return_date": return_date}
    if category:
        params["category"] = category
    if min_seats:
        params["seats"] = min_seats

    with httpx.Client() as client:
        response = client.get(f"{API_BASE_URL}/vehicles/available", headers=get_headers(), params=params)
        if response.status_code == 200:
            vehicles = response.json()
            if not vehicles:
                return f"No vehicles available from {pickup_date} to {return_date}."
            result = f"Available vehicles from {pickup_date} to {return_date}:\n"
            for v in vehicles:
                result += f"- ID {v['id']}: {v['year']} {v['make']} {v['model']} ({v['category']}) - {v['seats']} seats - ${v['daily_rate']}/day\n"
            return result
        return f"Error: {response.status_code} - {response.text}"


@tool
def get_vehicle_details(vehicle_id: int) -> str:
    """Get detailed information about a specific vehicle.

    Args:
        vehicle_id: The ID of the vehicle
    """
    with httpx.Client() as client:
        response = client.get(f"{API_BASE_URL}/vehicles/{vehicle_id}", headers=get_headers())
        if response.status_code == 200:
            v = response.json()
            return f"Vehicle Details:\n- ID: {v['id']}\n- Plate: {v['plate_number']}\n- {v['year']} {v['make']} {v['model']}\n- Category: {v['category']}\n- Seats: {v['seats']}\n- Daily Rate: ${v['daily_rate']}\n- Status: {v['status']}"
        elif response.status_code == 404:
            return f"Vehicle with ID {vehicle_id} not found."
        return f"Error: {response.status_code} - {response.text}"


@tool
def get_price_quote(vehicle_id: int, pickup_date: str, return_date: str) -> str:
    """Get a price quote for renting a specific vehicle.

    Args:
        vehicle_id: The ID of the vehicle
        pickup_date: Pickup date in YYYY-MM-DD format
        return_date: Return date in YYYY-MM-DD format
    """
    params = {"vehicle_id": vehicle_id, "pickup_date": pickup_date, "return_date": return_date}

    with httpx.Client() as client:
        response = client.get(f"{API_BASE_URL}/pricing", headers=get_headers(), params=params)
        if response.status_code == 200:
            p = response.json()
            return f"Price Quote:\n- Vehicle: {p['year'] if 'year' in p else ''} {p['make']} {p['model']} ({p['category']})\n- Dates: {p['pickup_date']} to {p['return_date']}\n- Duration: {p['num_days']} days\n- Daily Rate: ${p['daily_rate']}\n- Total Price: ${p['total_price']}"
        return f"Error: {response.status_code} - {response.text}"


@tool
def create_rental(vehicle_id: int, customer_name: str, customer_email: str, pickup_date: str, return_date: str) -> str:
    """Create a new car rental reservation.

    Args:
        vehicle_id: The ID of the vehicle to rent
        customer_name: Customer's full name
        customer_email: Customer's email address
        pickup_date: Pickup date in YYYY-MM-DD format
        return_date: Return date in YYYY-MM-DD format
    """
    payload = {
        "vehicle_id": vehicle_id,
        "customer_name": customer_name,
        "customer_email": customer_email,
        "pickup_date": pickup_date,
        "return_date": return_date
    }

    with httpx.Client() as client:
        response = client.post(f"{API_BASE_URL}/rentals", headers=get_headers(), json=payload)
        if response.status_code == 201:
            r = response.json()
            return f"Rental Confirmed!\n- Confirmation ID: {r['id']}\n- Vehicle: {r['make']} {r['model']} ({r['plate_number']})\n- Customer: {r['customer_name']} ({r['customer_email']})\n- Dates: {r['pickup_date']} to {r['return_date']}\n- Total: ${r['total_price']}\n- Status: {r['status']}"
        elif response.status_code == 409:
            return "Error: Vehicle is not available for the requested dates."
        return f"Error: {response.status_code} - {response.text}"


@tool
def list_rentals(status: Optional[str] = None) -> str:
    """List all rental reservations.

    Args:
        status: Filter by status (confirmed, cancelled, completed)
    """
    params = {}
    if status:
        params["status"] = status

    with httpx.Client() as client:
        response = client.get(f"{API_BASE_URL}/rentals", headers=get_headers(), params=params)
        if response.status_code == 200:
            rentals = response.json()
            if not rentals:
                return "No rentals found."
            result = f"Found {len(rentals)} rental(s):\n"
            for r in rentals:
                result += f"- ID {r['id']}: {r['make']} {r['model']} for {r['customer_name']} ({r['pickup_date']} to {r['return_date']}) - ${r['total_price']} - {r['status']}\n"
            return result
        return f"Error: {response.status_code} - {response.text}"


@tool
def get_rental_details(rental_id: int) -> str:
    """Get details of a specific rental reservation.

    Args:
        rental_id: The ID of the rental
    """
    with httpx.Client() as client:
        response = client.get(f"{API_BASE_URL}/rentals/{rental_id}", headers=get_headers())
        if response.status_code == 200:
            r = response.json()
            return f"Rental Details:\n- ID: {r['id']}\n- Vehicle: {r['make']} {r['model']} ({r['plate_number']})\n- Category: {r['category']}\n- Customer: {r['customer_name']} ({r['customer_email']})\n- Dates: {r['pickup_date']} to {r['return_date']}\n- Total: ${r['total_price']}\n- Status: {r['status']}\n- Created: {r['created_at']}"
        elif response.status_code == 404:
            return f"Rental with ID {rental_id} not found."
        return f"Error: {response.status_code} - {response.text}"


@tool
def cancel_rental(rental_id: int) -> str:
    """Cancel a rental reservation.

    Args:
        rental_id: The ID of the rental to cancel
    """
    with httpx.Client() as client:
        response = client.delete(f"{API_BASE_URL}/rentals/{rental_id}", headers=get_headers())
        if response.status_code == 200:
            r = response.json()
            return f"Rental {rental_id} has been cancelled.\n- Vehicle: {r['make']} {r['model']}\n- Customer: {r['customer_name']}\n- Status: {r['status']}"
        elif response.status_code == 400:
            return "Error: Rental is already cancelled."
        elif response.status_code == 404:
            return f"Rental with ID {rental_id} not found."
        return f"Error: {response.status_code} - {response.text}"


# === Agno Agent Setup ===

CAR_RENTAL_TOOLS = [
    get_categories,
    get_vehicles,
    check_availability,
    get_vehicle_details,
    get_price_quote,
    create_rental,
    list_rentals,
    get_rental_details,
    cancel_rental,
]


def create_car_rental_agent(openai_api_key: str) -> Agent:
    """Create the Agno car rental agent with all tools."""
    return Agent(
        model=OpenAIChat(id="gpt-4o-mini", api_key=openai_api_key),
        tools=CAR_RENTAL_TOOLS,
        instructions=[
            "You are a car rental provider agent that helps with vehicle rentals.",
            "You can search for available vehicles, get pricing, make reservations, and manage bookings.",
            "Always be helpful and provide clear, concise information.",
            "When searching for vehicles, suggest checking availability with specific dates.",
            "For bookings, always confirm the customer name and email.",
            "Keep responses short and data-focused - another agent will format them for users.",
        ],
        markdown=False,
        show_tool_calls=False,
    )


# === Orca Integration ===

async def process_message(data: ChatMessage):
    handler = OrcaHandler()
    session = handler.begin(data)

    try:
        variables = Variables(data.variables)
        openai_key = variables.get("OPENAI_API_KEY")

        if not openai_key:
            session.stream("Error: OPENAI_API_KEY not configured in Orca variables.")
            session.close()
            return

        session.loading.start("Processing your car rental request...")

        # Create Agno agent and run the query
        agent = create_car_rental_agent(openai_key)
        user_message = data.message

        # Run the agent
        response = agent.run(user_message)

        session.loading.end("Processing your car rental request...")

        # Stream the response
        if response and response.content:
            session.stream(response.content)
        else:
            session.stream("I couldn't process that request. Please try again.")

        session.close()

    except Exception as e:
        logger.exception("Error processing message")
        session.error("Something went wrong with the car rental agent.", exception=e)


app, orca = create_agent_app(
    process_message_func=process_message,
    title="Car Rental Provider Agent",
    description="AI-powered car rental agent for searching vehicles, checking availability, getting quotes, and managing reservations.",
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
