import requests
import time
from typing import Optional, Dict, Any

class RestAPI:
    """
    A robust, generic wrapper for handling REST API calls with automatic retries.
    """

    @staticmethod
    def request(
        url: str, 
        method: str = "POST", 
        headers: Optional[Dict[str, str]] = None, 
        payload: Optional[Dict[str, Any]] = None, 
        timeout: int = 30,
        max_retries: int = 3,
        retry_delay: int = 2
    ) -> Optional[Dict[str, Any]]:
        """
        Executes a REST API request with retry logic for failures.
        
        Args:
            url (str): The full URL or endpoint.
            method (str): "GET", "POST", "PUT", "DELETE".
            headers (dict): Authorization and content headers.
            payload (dict): The JSON body for POST/PUT requests.
            timeout (int): Seconds to wait before failing.
            max_retries (int): Number of times to retry on 5xx/Timeout.
            retry_delay (int): Seconds to wait between retries.

        Returns:
            dict: The JSON response if successful, or None if failed.
        """
        method = method.upper()

        for attempt in range(1, max_retries + 1):
            try:
                if attempt > 1:
                    print(f"   🔄 Retry {attempt}/{max_retries}...")

                response = requests.request(
                    method=method,
                    url=url,
                    json=payload if method in ["POST", "PUT"] else None,
                    params=payload if method == "GET" else None,
                    headers=headers,
                    timeout=timeout
                )

                # Check for HTTP errors
                response.raise_for_status()

                # If successful, return JSON
                return response

            except requests.exceptions.HTTPError as e:
                # 🛑 4xx Errors (Client Side) -> Do NOT Retry (e.g., Wrong Password, Bad Prompt)
                if 400 <= response.status_code < 500:
                    print(f"❌ API Client Error ({response.status_code}): {response.text}")
                    return None
                
                # ⚠️ 5xx Errors (Server Side) -> RETRY (e.g., Server Overloaded)
                print(f"⚠️ API Server Error ({response.status_code}).")
                
            except requests.exceptions.Timeout:
                print(f"⚠️ API Timeout ({timeout}s).")
                
            except requests.exceptions.ConnectionError:
                print(f"⚠️ API Connection Failed.")
                
            except Exception as e:
                print(f"❌ Unexpected Error: {e}")
                return None # Unknown error, safest to stop

            # If we are here, it means we hit a Retry-able error (5xx, Timeout, Connection)
            if attempt < max_retries:
                time.sleep(retry_delay)
            else:
                print(f"❌ API Failed after {max_retries} attempts.")
                return None
        
        return None