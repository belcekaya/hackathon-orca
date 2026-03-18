# Car Rental Provider Agent

AI-powered car rental agent built with **Agno Framework** and **Orca SDK** for the MADHACK x Orca Hackathon.

## Features

- Search vehicle categories and fleet
- Check availability for date ranges
- Get price quotes
- Create rental reservations
- List and manage bookings
- Cancel reservations

## Tech Stack

- **Agno Framework** - AI agent with tool calling
- **Orca SDK** - Platform integration
- **OpenAI GPT-4o-mini** - LLM backend
- **FastAPI/Uvicorn** - HTTP server

## Quick Start

```bash
cd src/hackathon-18march-boilerplate/provider
pip install -r requirements.txt
python main.py
# Runs on http://localhost:8000
```

## Orca Configuration

1. Register agent in Orca admin panel
2. Set URL: `https://YOUR-NGROK-URL/api/v1/send_message`
3. Add variable: `MADHACK-OPENAI-KEY` with your OpenAI API key

## API Endpoints

The agent connects to the Car Rental API:
- `GET /api/categories` - List vehicle categories
- `GET /api/vehicles` - List all vehicles
- `GET /api/vehicles/available` - Check availability
- `GET /api/pricing` - Get price quote
- `POST /api/rentals` - Create reservation
- `GET /api/rentals` - List reservations
- `DELETE /api/rentals/{id}` - Cancel reservation

## Tools Available

| Tool | Description |
|------|-------------|
| `get_categories` | List vehicle categories with rates |
| `get_vehicles` | List fleet (filter by category/seats) |
| `check_availability` | Find available vehicles for dates |
| `get_vehicle_details` | Get specific vehicle info |
| `get_price_quote` | Calculate rental cost |
| `create_rental` | Book a vehicle |
| `list_rentals` | View all reservations |
| `get_rental_details` | Get booking details |
| `cancel_rental` | Cancel a reservation |

## Team

Built for MADHACK x Orca AI Agent Hackathon - March 2026
