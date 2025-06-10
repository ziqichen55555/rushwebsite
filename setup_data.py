import os
import django
from django.utils import timezone

# Setup Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "rush_car_rental.settings")
django.setup()

from django.contrib.auth.models import User
from locations.models import State, Location, CityHighlight
from cars.models import CarCategory, Car, CarFeature, VehicleType, VehicleCategoryType, VehicleCategory
from accounts.models import Profile
from bookings.models import Booking

# Create States
def create_states():
    states = [
        {"name": "Victoria", "code": "VIC"},
        {"name": "New South Wales", "code": "NSW"},
        {"name": "Queensland", "code": "QLD"},
        {"name": "Western Australia", "code": "WA"},
        {"name": "South Australia", "code": "SA"},
        {"name": "Tasmania", "code": "TAS"},
        {"name": "Australian Capital Territory", "code": "ACT"},
        {"name": "Northern Territory", "code": "NT"},
    ]
    
    for state_data in states:
        State.objects.get_or_create(
            code=state_data["code"],
            defaults={"name": state_data["name"]}
        )
    
    print(f"Added {len(states)} states")

# Create Car Categories
def create_car_categories():
    """Create car categories"""
    print("Creating car categories...")
    
    # Create vehicle types first
    vehicle_types = {
        'PETROL': 'Petrol vehicles',
        'HYBRID': 'Hybrid vehicles',
        'ELECTRIC': 'Electric vehicles'
    }
    
    for type_name, description in vehicle_types.items():
        VehicleType.objects.get_or_create(
            name=type_name,
            defaults={'description': description}
        )
    
    # Create vehicle category types
    category_types = [
        {
            'category_type': 'Economy',
            'rate_type': 'DAILY',
            'web_available': True,
            'ordering': 1
        },
        {
            'category_type': 'Compact',
            'rate_type': 'DAILY',
            'web_available': True,
            'ordering': 2
        },
        {
            'category_type': 'Midsize',
            'rate_type': 'DAILY',
            'web_available': True,
            'ordering': 3
        },
        {
            'category_type': 'SUV',
            'rate_type': 'DAILY',
            'web_available': True,
            'ordering': 4
        },
        {
            'category_type': 'Luxury',
            'rate_type': 'DAILY',
            'web_available': True,
            'ordering': 5
        }
    ]
    
    for type_data in category_types:
        VehicleCategoryType.objects.get_or_create(
            category_type=type_data['category_type'],
            defaults={
                'rate_type': type_data['rate_type'],
                'web_available': type_data['web_available'],
                'ordering': type_data['ordering'],
                'created_at': timezone.now(),
                'updated_at': timezone.now()
            }
        )
    
    # Create test vehicles
    test_vehicles = [
        {
            'name': 'Toyota Corolla',
            'vehicle_category': 'Toyota Corolla',
            'category_type': 'Economy',
            'vehicle_type': 'PETROL',
            'daily_rate': 50.00,
            'num_adults': 4,
            'num_children': 1,
            'num_large_case': 2,
            'num_small_case': 2,
            'renting_category': True,
            'is_available': True
        },
        {
            'name': 'Honda Civic',
            'vehicle_category': 'Honda Civic',
            'category_type': 'Compact',
            'vehicle_type': 'HYBRID',
            'daily_rate': 60.00,
            'num_adults': 4,
            'num_children': 1,
            'num_large_case': 2,
            'num_small_case': 2,
            'renting_category': True,
            'is_available': True
        },
        {
            'name': 'Toyota Camry',
            'vehicle_category': 'Toyota Camry',
            'category_type': 'Midsize',
            'vehicle_type': 'PETROL',
            'daily_rate': 70.00,
            'num_adults': 5,
            'num_children': 0,
            'num_large_case': 3,
            'num_small_case': 2,
            'renting_category': True,
            'is_available': True
        },
        {
            'name': 'Toyota RAV4',
            'vehicle_category': 'Toyota RAV4',
            'category_type': 'SUV',
            'vehicle_type': 'HYBRID',
            'daily_rate': 80.00,
            'num_adults': 5,
            'num_children': 0,
            'num_large_case': 4,
            'num_small_case': 2,
            'renting_category': True,
            'is_available': True
        },
        {
            'name': 'Tesla Model 3',
            'vehicle_category': 'Tesla Model 3',
            'category_type': 'Luxury',
            'vehicle_type': 'ELECTRIC',
            'daily_rate': 100.00,
            'num_adults': 5,
            'num_children': 0,
            'num_large_case': 3,
            'num_small_case': 2,
            'renting_category': True,
            'is_available': True
        },
        {
            'name': 'BMW 3 Series',
            'vehicle_category': 'BMW 3 Series',
            'category_type': 'Luxury',
            'vehicle_type': 'PETROL',
            'daily_rate': 90.00,
            'num_adults': 5,
            'num_children': 0,
            'num_large_case': 3,
            'num_small_case': 2,
            'renting_category': True,
            'is_available': True
        }
    ]
    
    for vehicle_data in test_vehicles:
        category_type = VehicleCategoryType.objects.get(category_type=vehicle_data['category_type'])
        vehicle_type = VehicleType.objects.get(name=vehicle_data['vehicle_type'])
        
        VehicleCategory.objects.get_or_create(
            vehicle_category=vehicle_data['vehicle_category'],
            defaults={
                'name': vehicle_data['name'],
                'category_type': category_type,
                'vehicle_type': vehicle_type,
                'daily_rate': vehicle_data['daily_rate'],
                'num_adults': vehicle_data['num_adults'],
                'num_children': vehicle_data['num_children'],
                'num_large_case': vehicle_data['num_large_case'],
                'num_small_case': vehicle_data['num_small_case'],
                'renting_category': vehicle_data['renting_category'],
                'is_available': vehicle_data['is_available']
            }
        )
    
    print("Added test vehicles")

# Create Locations
def create_locations():
    # Get state objects
    vic = State.objects.get(code="VIC")
    nsw = State.objects.get(code="NSW")
    qld = State.objects.get(code="QLD")
    wa = State.objects.get(code="WA")
    
    locations = [
        {
            "name": "Melbourne Airport",
            "address": "Arrival Drive, Melbourne Airport",
            "city": "Melbourne",
            "state": vic,
            "postal_code": "3045",
            "phone": "(03) 9338 0000",
            "email": "melb.airport@rushcarrental.com",
            "is_airport": True,
            "opening_hours": "Monday-Sunday: 6AM-11PM",
            "latitude": -37.669,
            "longitude": 144.849,
        },
        {
            "name": "Melbourne CBD",
            "address": "150 Queen Street",
            "city": "Melbourne",
            "state": vic,
            "postal_code": "3000",
            "phone": "(03) 9600 1234",
            "email": "melb.cbd@rushcarrental.com",
            "is_airport": False,
            "opening_hours": "Monday-Friday: 8AM-6PM, Saturday: 9AM-5PM, Sunday: 10AM-4PM",
            "latitude": -37.816,
            "longitude": 144.961,
        },
        {
            "name": "Sydney Airport",
            "address": "Keith Smith Avenue, Mascot",
            "city": "Sydney",
            "state": nsw,
            "postal_code": "2020",
            "phone": "(02) 9667 0000",
            "email": "syd.airport@rushcarrental.com",
            "is_airport": True,
            "opening_hours": "Monday-Sunday: 6AM-11PM",
            "latitude": -33.939,
            "longitude": 151.175,
        },
        {
            "name": "Sydney CBD",
            "address": "55 Market Street",
            "city": "Sydney",
            "state": nsw,
            "postal_code": "2000",
            "phone": "(02) 9234 5678",
            "email": "syd.cbd@rushcarrental.com",
            "is_airport": False,
            "opening_hours": "Monday-Friday: 8AM-6PM, Saturday: 9AM-5PM, Sunday: Closed",
            "latitude": -33.870,
            "longitude": 151.207,
        },
        {
            "name": "Brisbane Airport",
            "address": "Airport Drive, Brisbane Airport",
            "city": "Brisbane",
            "state": qld,
            "postal_code": "4008",
            "phone": "(07) 3406 0000",
            "email": "bne.airport@rushcarrental.com",
            "is_airport": True,
            "opening_hours": "Monday-Sunday: 5AM-11PM",
            "latitude": -27.384,
            "longitude": 153.117,
        },
        {
            "name": "Perth Airport",
            "address": "Terminal 1, Perth Airport",
            "city": "Perth",
            "state": wa,
            "postal_code": "6105",
            "phone": "(08) 9478 0000",
            "email": "per.airport@rushcarrental.com",
            "is_airport": True,
            "opening_hours": "Monday-Sunday: 6AM-10PM",
            "latitude": -31.940,
            "longitude": 115.967,
        },
    ]
    
    for loc_data in locations:
        Location.objects.get_or_create(
            name=loc_data["name"],
            defaults={
                "address": loc_data["address"],
                "city": loc_data["city"],
                "state": loc_data["state"],
                "postal_code": loc_data["postal_code"],
                "phone": loc_data["phone"],
                "email": loc_data["email"],
                "is_airport": loc_data["is_airport"],
                "opening_hours": loc_data["opening_hours"],
                "latitude": loc_data["latitude"],
                "longitude": loc_data["longitude"],
            }
        )
    
    print(f"Added {len(locations)} locations")

# Create City Highlights
def create_city_highlights():
    # Get state objects
    vic = State.objects.get(code="VIC")
    nsw = State.objects.get(code="NSW")
    qld = State.objects.get(code="QLD")
    
    highlights = [
        {
            "city": "Melbourne",
            "state": vic,
            "description": "Explore Melbourne's famous laneways, world-class restaurants, and vibrant arts scene. Just a short drive away is the Great Ocean Road with its stunning coastal views.",
            "image_url": "https://images.unsplash.com/photo-1514395462725-fb4566210144",
        },
        {
            "city": "Sydney",
            "state": nsw,
            "description": "Visit the iconic Sydney Opera House, beautiful beaches like Bondi, and the stunning Sydney Harbour. Perfect for a weekend getaway or extended stay.",
            "image_url": "https://images.unsplash.com/photo-1506973035872-a4ec16b8e8d9",
        },
        {
            "city": "Brisbane",
            "state": qld,
            "description": "Enjoy Brisbane's year-round warm climate, outdoor lifestyle, and proximity to the Gold Coast. The perfect starting point for Queensland adventures.",
            "image_url": "https://images.unsplash.com/photo-1566734904496-9309bb1798b5",
        },
    ]
    
    for highlight_data in highlights:
        CityHighlight.objects.get_or_create(
            city=highlight_data["city"],
            state=highlight_data["state"],
            defaults={
                "description": highlight_data["description"],
                "image_url": highlight_data["image_url"],
            }
        )
    
    print(f"Added {len(highlights)} city highlights")

# Create Cars
def create_cars():
    # Get categories and locations
    economy = CarCategory.objects.get(name="Economy")
    compact = CarCategory.objects.get(name="Compact")
    midsize = CarCategory.objects.get(name="Midsize")
    suv = CarCategory.objects.get(name="SUV")
    luxury = CarCategory.objects.get(name="Luxury")
    sports = CarCategory.objects.get(name="Sports Car")
    
    melbourne_airport = Location.objects.get(name="Melbourne Airport")
    melbourne_cbd = Location.objects.get(name="Melbourne CBD")
    sydney_airport = Location.objects.get(name="Sydney Airport")
    sydney_cbd = Location.objects.get(name="Sydney CBD")
    brisbane_airport = Location.objects.get(name="Brisbane Airport")
    perth_airport = Location.objects.get(name="Perth Airport")
    
    cars = [
        {
            "name": "Toyota Corolla",
            "make": "Toyota",
            "model": "Corolla",
            "year": 2023,
            "category": economy,
            "seats": 5,
            "bags": 2,
            "doors": 4,
            "transmission": "A",
            "air_conditioning": True,
            "image_url": "https://images.unsplash.com/photo-1626668893632-6f3a4466d222",
            "daily_rate": 65.00,
            "comparison_provider1_name": "RentalCars",
            "comparison_provider1_rate": 72.00,
            "comparison_provider2_name": "CarHire",
            "comparison_provider2_rate": 70.00,
            "locations": [melbourne_airport, melbourne_cbd, sydney_airport, sydney_cbd],
            "features": ["Bluetooth Connectivity", "Backup Camera", "USB Ports", "Cruise Control"]
        },
        {
            "name": "Mazda 3",
            "make": "Mazda",
            "model": "3",
            "year": 2023,
            "category": compact,
            "seats": 5,
            "bags": 3,
            "doors": 4,
            "transmission": "A",
            "air_conditioning": True,
            "image_url": "https://images.unsplash.com/photo-1541899481282-d53bffe3c35d",
            "daily_rate": 70.00,
            "comparison_provider1_name": "RentalCars",
            "comparison_provider1_rate": 78.00,
            "comparison_provider2_name": "CarHire",
            "comparison_provider2_rate": 75.00,
            "locations": [melbourne_airport, melbourne_cbd, sydney_airport, brisbane_airport],
            "features": ["Apple CarPlay/Android Auto", "Keyless Entry", "Alloy Wheels", "LED Headlights"]
        },
        {
            "name": "Toyota Camry",
            "make": "Toyota",
            "model": "Camry",
            "year": 2023,
            "category": midsize,
            "seats": 5,
            "bags": 4,
            "doors": 4,
            "transmission": "A",
            "air_conditioning": True,
            "image_url": "https://images.unsplash.com/photo-1590902895434-b115b8467979",
            "daily_rate": 85.00,
            "comparison_provider1_name": "RentalCars",
            "comparison_provider1_rate": 94.00,
            "comparison_provider2_name": "CarHire",
            "comparison_provider2_rate": 92.00,
            "locations": [melbourne_airport, sydney_airport, brisbane_airport, perth_airport],
            "features": ["Leather Seats", "Push Button Start", "Dual Climate Control", "Lane Departure Warning"]
        },
        {
            "name": "Mazda CX-5",
            "make": "Mazda",
            "model": "CX-5",
            "year": 2023,
            "category": suv,
            "seats": 5,
            "bags": 5,
            "doors": 5,
            "transmission": "A",
            "air_conditioning": True,
            "image_url": "https://images.unsplash.com/photo-1577471488278-16eec37ffcc2",
            "daily_rate": 95.00,
            "comparison_provider1_name": "RentalCars",
            "comparison_provider1_rate": 105.00,
            "comparison_provider2_name": "CarHire",
            "comparison_provider2_rate": 102.00,
            "locations": [melbourne_airport, sydney_airport, sydney_cbd, brisbane_airport, perth_airport],
            "features": ["All-Wheel Drive", "Panoramic Sunroof", "Premium Sound System", "Power Liftgate"]
        },
        {
            "name": "BMW 3 Series",
            "make": "BMW",
            "model": "3 Series",
            "year": 2023,
            "category": luxury,
            "seats": 5,
            "bags": 3,
            "doors": 4,
            "transmission": "A",
            "air_conditioning": True,
            "image_url": "https://images.unsplash.com/photo-1556189250-72ba954cfc2b",
            "daily_rate": 150.00,
            "comparison_provider1_name": "RentalCars",
            "comparison_provider1_rate": 170.00,
            "comparison_provider2_name": "CarHire",
            "comparison_provider2_rate": 165.00,
            "locations": [melbourne_airport, sydney_airport],
            "features": ["Premium Leather Interior", "Harman Kardon Sound", "Heated Seats", "Adaptive Cruise Control"]
        },
        {
            "name": "Ford Mustang",
            "make": "Ford",
            "model": "Mustang",
            "year": 2023,
            "category": sports,
            "seats": 4,
            "bags": 2,
            "doors": 2,
            "transmission": "A",
            "air_conditioning": True,
            "image_url": "https://images.unsplash.com/photo-1584345604476-8ec5e12e42dd",
            "daily_rate": 180.00,
            "comparison_provider1_name": "RentalCars",
            "comparison_provider1_rate": 200.00,
            "comparison_provider2_name": "CarHire",
            "comparison_provider2_rate": 195.00,
            "locations": [melbourne_airport, sydney_airport],
            "features": ["V8 Engine", "Sport Mode", "Launch Control", "Performance Brakes"]
        },
    ]
    
    for car_data in cars:
        # Create the car
        car, created = Car.objects.get_or_create(
            name=car_data["name"],
            make=car_data["make"],
            model=car_data["model"],
            year=car_data["year"],
            defaults={
                "category": car_data["category"],
                "seats": car_data["seats"],
                "bags": car_data["bags"],
                "doors": car_data["doors"],
                "transmission": car_data["transmission"],
                "air_conditioning": car_data["air_conditioning"],
                "image_url": car_data["image_url"],
                "daily_rate": car_data["daily_rate"],
                "comparison_provider1_name": car_data["comparison_provider1_name"],
                "comparison_provider1_rate": car_data["comparison_provider1_rate"],
                "comparison_provider2_name": car_data["comparison_provider2_name"],
                "comparison_provider2_rate": car_data["comparison_provider2_rate"],
            }
        )
        
        # Add locations for the car if it was created
        if created:
            car.locations.set(car_data["locations"])
            
            # Add features
            for feature in car_data["features"]:
                CarFeature.objects.create(
                    car=car,
                    feature=feature
                )
    
    print(f"Added {len(cars)} cars")

if __name__ == "__main__":
    print("Starting data setup...")
    create_states()
    create_car_categories()
    create_locations()
    create_city_highlights()
    create_cars()
    print("Data setup complete!")