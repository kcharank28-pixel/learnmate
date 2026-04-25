import requests

# Example Student
student = {
    "user_id": "chidvilas006",
    "password": "5051",
    "role": "student",
    "name": "chidvilas",
    "email": "ni@student.com",
    "branch": "CSE",
    "year": 2
}

# Example Faculty
faculty = {
    "user_id": "fac001",
    "password": "654321",
    "role": "faculty",
    "name": "Dr. Rao",
    "email": "rao@faculty.com",
    "branch": "CSE",
    "year": 0
}

# Change this if you're hosting online
URL = "http://127.0.0.1:5000/register"

# Register both
print(requests.post(URL, json=student).json())
print(requests.post(URL, json=faculty).json())