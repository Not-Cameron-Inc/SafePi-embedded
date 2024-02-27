import requests

# URL of the endpoint
url = "https://www.safepi.org/create_user"

# JSON data to be sent in the request body
data = {
    "email": "test@test.com",
    "password": "TheWorstPaor1209"
}

# Headers specifying content type
headers = {
    "Content-Type": "application/json"
}

# Sending POST request
response = requests.post(url, json=data, headers=headers, verify="../keys/cert-remote.pem")

# Printing the response
print(response.text)
