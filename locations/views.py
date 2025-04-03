from django.shortcuts import render
from .models import Location, State, CityHighlight

def location_list(request):
    states = State.objects.all()
    state_filter = request.GET.get('state', '')
    
    if state_filter:
        locations = Location.objects.filter(state__code=state_filter)
    else:
        locations = Location.objects.all()
    
    return render(request, 'locations/locations_list.html', {
        'locations': locations,
        'states': states,
        'current_state': state_filter
    })

def city_highlights(request):
    highlights = CityHighlight.objects.all()
    return render(request, 'locations/city_highlights.html', {'highlights': highlights})
