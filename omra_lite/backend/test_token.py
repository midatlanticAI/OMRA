import aiohttp
import asyncio
import json
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

async def test_token_endpoint():
    print("=== Testing Token Endpoint ===")
    url = "http://localhost:8000/token"
    data = {"username": "admin", "password": "admin1"}
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(
                url, 
                data=data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            ) as response:
                status = response.status
                print(f"Status: {status}")
                if status == 200:
                    result = await response.json()
                    print(f"Response: {json.dumps(result, indent=2)}")
                    
                    # Test the users/me endpoint
                    token = result.get("access_token")
                    if token:
                        print("\n=== Testing /users/me Endpoint ===")
                        headers = {"Authorization": f"Bearer {token}"}
                        print(f"Request headers: {headers}")
                        
                        try:
                            async with session.get("http://localhost:8000/users/me", headers=headers) as me_response:
                                me_status = me_response.status
                                print(f"Status: {me_status}")
                                response_text = await me_response.text()
                                print(f"Raw response: {response_text}")
                                
                                if me_status == 200:
                                    try:
                                        me_result = json.loads(response_text)
                                        print(f"User Data: {json.dumps(me_result, indent=2)}")
                                    except json.JSONDecodeError:
                                        print("Failed to parse JSON response")
                                else:
                                    print(f"Error accessing /users/me endpoint")
                        except Exception as e:
                            print(f"Exception during /users/me request: {str(e)}")
                            logger.exception("Error in /users/me request")
                else:
                    print(f"Error: {await response.text()}")
        except Exception as e:
            print(f"Exception: {str(e)}")
            logger.exception("Error in token request")

if __name__ == "__main__":
    asyncio.run(test_token_endpoint()) 