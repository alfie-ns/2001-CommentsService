import requests
import json

# External authentication API URL
AUTH_API_URL = "https://web.socem.plymouth.ac.uk/COMP2001/auth/api/users"

def authenticate_user(email, password):
    """
    Authenticate user against external API.
    Returns tuple (authenticated, is_admin) if successful, (False, False) otherwise.
    
    API expects email and password in JSON format.
    API returns ["Verified","True"/"False"] format.
    """
    try:
        print(f"Attempting to authenticate user: {email}")
        
        # POST request to authenticate
        
        # No longer need to escape exclamation marks as the API was fixed the same day I was doing this in fact
        payload = json.dumps({
            "email": email,
            "password": password
        })
        
        response = requests.post(
            AUTH_API_URL,
            data=payload,
            headers={
                "Content-Type": "application/json"
            },
            timeout=10
        )
        
        print(f"Auth API response status: {response.status_code}")
        print(f"Auth API response: {response.text}")
        
        if response.status_code == 200:
            # API returns ["Verified","True"/"False"] format
            result = response.json()
            if isinstance(result, list) and len(result) >= 2:
                # The API returns ["Verified","True"/"False"] format
                if result[0] == "Verified":
                    if result[1] == "True":
                        print(f"Authentication successful for {email}")
                        # Check if user is admin (Grace Hopper)
                        is_admin = email == 'grace@plymouth.ac.uk'
                        return True, is_admin
                    else:
                        print(f"Authentication failed for {email}")
                        return False, False
                else:
                    print(f"ERROR: Unexpected API response format: {result}")
                    return False, False
            else:
                print(f"WARNING: Unexpected API response format: {result}")
                return False, False
        else:
            print(f"WARNING: Authentication failed for {email}: {response.status_code}")
            return False, False
            
    except requests.RequestException as e:
        print(f"ERROR: Authentication API error: {str(e)}")
        return False, False


def get_authenticated_user(request):
    """
    Extract authenticated user from request.
    Returns user email and whether they're admin.
    
    For the coursework, we're using Basic Auth with the external API.
    """
    # Check for Authorization header
    auth_header = request.headers.get('Authorization', '')
    print(f"Auth header received: {auth_header[:20] if auth_header else 'None'}...")  # log first 20 chars
    
    if auth_header and auth_header.startswith('Basic '):
        # Decode Basic auth
        import base64
        try:
            credentials = base64.b64decode(auth_header[6:]).decode('utf-8')
            email, password = credentials.split(':', 1)
            
            # Authenticate against external API
            verified, is_admin = authenticate_user(email, password)
            if verified:
                return email, is_admin
            else:
                print(f"WARNING: Failed Basic auth for {email}")
                return None, False
        except Exception as e:
            print(f"ERROR: Basic auth decode error: {str(e)}")
            return None, False
    
    return None, False