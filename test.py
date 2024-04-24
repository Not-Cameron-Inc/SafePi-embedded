import requests

# Define the URL of the endpoint
url = 'https://safepi.org/token'

# Define the headers
headers = {
    'Authorization': 'Basic MTI0NTQyNDQyMzI3LXIwNTYwYjVldmVxYW9hczM2NWg5ZnNicDVxaDJuMTdoLmFwcHMuZ29vZ2xldXNlcmNvbnRlbnQuY29tOkdPQ1NQWC00RUl6NXo0dzdhQlRiRFpwWDQxVHM0UnVRRHE1',
    'Content-Type': 'application/x-www-form-urlencoded'
}

# Define the data
data = {
    'grant_type': 'client_credentials',
    'scope': 'read'
}

# Make the POST request
response = requests.post(url, headers=headers, data=data)

# Print the response content
print("Response:")
print(response.text)
