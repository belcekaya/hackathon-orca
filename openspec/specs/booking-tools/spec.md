# Booking APIs

APIs mock de reservas del hackathon. El Provider agent las consume via HTTP (httpx/requests).

## Context

6 servicios de viaje con 9 instancias independientes. Auth via header `X-API-Key`. Cada equipo tiene asignada(s) API(s) específicas.

**Base URL**: `https://hacketon-18march-api.orcaplatform.ai`

## Services & Keys

| Service | Path prefix | API Key |
|---------|------------|---------|
| Hotel 1 | `/hotel-1/api` | `hotel-1-key-abc123` |
| Hotel 2 | `/hotel-2/api` | `hotel-2-key-def456` |
| Restaurant 1 | `/restaurant-1/api` | `restaurant-1-key-ghi789` |
| Restaurant 2 | `/restaurant-2/api` | `restaurant-2-key-jkl012` |
| Restaurant 3 | `/restaurant-3/api` | `restaurant-3-key-mno345` |
| Flight 1 | `/flight-1/api` | `flight-1-key-pqr678` |
| Car Rental 1 | `/car-rental-1/api` | `car-rental-1-key-stu901` |
| Tour Guide 1 | `/tour-guide-1/api` | `tour-guide-1-key-vwx234` |
| Museum 1 | `/museum-1/api` | `museum-1-key-yza567` |

Schema endpoint: `GET /{service}/api/schema` (self-describing JSON manifest)

## Hotel API (2 instances)

Room reservations, date-range pricing with weekend surcharges, capacity management.

| Method | Path | Description | Params/Body |
|--------|------|-------------|-------------|
| GET | `/api/rooms` | List all rooms | — |
| GET | `/api/rooms/available` | Available rooms for dates | `check_in`, `check_out` (required), `guests` (optional) |
| GET | `/api/pricing` | Price quote with per-night breakdown | `room_id`, `check_in`, `check_out` (required) |
| POST | `/api/reservations` | Create reservation | `room_id`, `guest_name`, `guest_email`, `check_in`, `check_out`, `num_guests` |
| GET | `/api/reservations` | List reservations | `status` (optional: confirmed/cancelled) |
| GET | `/api/reservations/{id}` | Get reservation by ID | — |
| DELETE | `/api/reservations/{id}` | Cancel reservation | — |

## Restaurant API (3 instances)

Table reservations, 6 time slots, party size validation, location filtering.

**Time slots**: 11:00, 12:30, 14:00, 18:00, 19:30, 21:00

| Method | Path | Description | Params/Body |
|--------|------|-------------|-------------|
| GET | `/api/tables` | List all tables | — |
| GET | `/api/tables/available` | Available tables | `date`, `time_slot` (required), `party_size` (optional) |
| GET | `/api/time-slots` | List valid time slots | — |
| POST | `/api/reservations` | Create reservation | `table_id`, `guest_name`, `guest_email`, `date`, `time_slot`, `party_size`, `special_requests` (opt) |
| GET | `/api/reservations` | List reservations | `date`, `status` (optional) |
| GET | `/api/reservations/{id}` | Get reservation by ID | — |
| DELETE | `/api/reservations/{id}` | Cancel reservation | — |

## Flight API — SkyMock Air (1 instance)

Flight bookings across 6 US cities, 3 seat classes, seat availability tracking.

**Seat classes**: economy (1x), business (2.5x), first (5x)

| Method | Path | Description | Params/Body |
|--------|------|-------------|-------------|
| GET | `/api/flights` | List flights | `origin`, `destination`, `date` (optional) |
| GET | `/api/flights/search` | Search available flights | `origin`, `destination` (required), `date`, `passengers` (optional) |
| GET | `/api/flights/{id}` | Get flight details | — |
| GET | `/api/pricing` | Price quote by class | `flight_id` (required), `seat_class`, `passengers` (optional) |
| POST | `/api/bookings` | Create booking | `flight_id`, `passenger_name`, `passenger_email`, `num_passengers`, `seat_class` |
| GET | `/api/bookings` | List bookings | `status` (optional) |
| GET | `/api/bookings/{id}` | Get booking by ID | — |
| DELETE | `/api/bookings/{id}` | Cancel booking | — |
| GET | `/api/destinations` | List all cities | — |

## Car Rental API (1 instance)

16-vehicle fleet across 7 categories, date-range availability, daily rate pricing.

**Categories**: economy, compact, midsize, fullsize, suv, premium, luxury

| Method | Path | Description | Params/Body |
|--------|------|-------------|-------------|
| GET | `/api/vehicles` | List vehicles | `category`, `seats` (optional) |
| GET | `/api/vehicles/available` | Available vehicles | `pickup_date`, `return_date` (required), `category`, `seats` (optional) |
| GET | `/api/vehicles/{id}` | Get vehicle details | — |
| GET | `/api/categories` | List categories with rates | — |
| GET | `/api/pricing` | Price quote | `vehicle_id`, `pickup_date`, `return_date` (required) |
| POST | `/api/rentals` | Create rental | `vehicle_id`, `customer_name`, `customer_email`, `pickup_date`, `return_date` |
| GET | `/api/rentals` | List rentals | `status` (optional) |
| GET | `/api/rentals/{id}` | Get rental by ID | — |
| DELETE | `/api/rentals/{id}` | Cancel rental | — |

## Tour Guide API (1 instance)

12 tours across 6 categories, difficulty levels, group size limits, per-person pricing.

**Categories**: cultural, adventure, food, nature, nightlife, historical
**Difficulty**: easy, moderate, challenging

| Method | Path | Description | Params/Body |
|--------|------|-------------|-------------|
| GET | `/api/tours` | List tours | `category`, `difficulty`, `max_price`, `location` (optional) |
| GET | `/api/tours/{id}` | Get tour details | — |
| GET | `/api/tours/available` | Check availability | `tour_id`, `date` (required), `guests` (optional) |
| GET | `/api/categories` | List categories | — |
| GET | `/api/pricing` | Price quote | `tour_id` (required), `guests` (optional) |
| POST | `/api/bookings` | Create booking | `tour_id`, `tour_date`, `guest_name`, `guest_email`, `num_guests` |
| GET | `/api/bookings` | List bookings | `status`, `date` (optional) |
| GET | `/api/bookings/{id}` | Get booking by ID | — |
| DELETE | `/api/bookings/{id}` | Cancel booking | — |

## Museum API (1 instance)

Timed-entry tickets, 4 time slots, 4 ticket types, visitor capacity per slot.

**Ticket types**: adult ($25), child ($12), senior ($18), student ($15)

| Method | Path | Description | Params/Body |
|--------|------|-------------|-------------|
| GET | `/api/time-slots` | List time slots with capacity | — |
| GET | `/api/availability` | Check availability by date | `date` (required), `time_slot_id`, `visitors` (optional) |
| GET | `/api/pricing` | Price quote | `ticket_type`, `visitors` (optional) |
| GET | `/api/ticket-types` | List ticket types with prices | — |
| POST | `/api/tickets` | Book tickets | `time_slot_id`, `visit_date`, `visitor_name`, `visitor_email`, `num_visitors`, `ticket_type` |
| GET | `/api/tickets` | List tickets | `date`, `status` (optional) |
| GET | `/api/tickets/{id}` | Get ticket by ID | — |
| DELETE | `/api/tickets/{id}` | Cancel ticket | — |
