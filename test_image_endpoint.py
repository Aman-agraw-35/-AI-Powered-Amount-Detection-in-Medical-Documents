import requests
import json
import sys

def test_image_extraction(image_path):
    url = "http://localhost:5000/api/v1/extract/image"
    
    try:
        with open(image_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(url, files=files)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response:")
        print(json.dumps(response.json(), indent=2))
        
    except FileNotFoundError:
        print(f"Error: Image file not found at {image_path}")
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to server. Make sure the server is running on http://localhost:5000")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    image_path = "images/input.png" if len(sys.argv) < 2 else sys.argv[1]
    test_image_extraction(image_path)


