import requests

def get_location_from_ip(ip_address):
    """
    Gets country, city, lat, lng from user's IP address.
    Uses ip-api.com — FREE, no API key needed, 45 requests/minute.
    """
    try:
        # Skip for localhost testing
        if ip_address in ('127.0.0.1', 'localhost', '::1'):
            return {
                'country':      'India',      # default for local testing
                'country_code': 'IN',
                'city':         'Ghaziabad',
                'latitude':     28.6692,
                'longitude':    77.4538
            }

        response = requests.get(
            f'http://ip-api.com/json/{ip_address}?fields=status,country,countryCode,city,lat,lon',
            timeout=5
        )
        data = response.json()

        if data.get('status') == 'success':
            return {
                'country':      data.get('country', 'Unknown'),
                'country_code': data.get('countryCode', 'UN'),
                'city':         data.get('city', 'Unknown'),
                'latitude':     data.get('lat', 0.0),
                'longitude':    data.get('lon', 0.0)
            }
    except Exception as e:
        print(f"Location lookup failed: {e}")

    return {
        'country': 'Unknown', 'country_code': 'UN',
        'city': 'Unknown', 'latitude': 0.0, 'longitude': 0.0
    }