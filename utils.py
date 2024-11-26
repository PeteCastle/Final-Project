import time
from httpx import HTTPTransport
def flatten_dict(d, parent_key='', sep='_'):
    """
    Flatten a nested dictionary.

    Args:
        d (dict): The dictionary to flatten.
        parent_key (str): The base key string for nested keys.
        sep (str): The separator between keys.

    Returns:
        dict: The flattened dictionary.
    """
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)

class RateLimitTransport(HTTPTransport):
    def __init__(self, rate_limit=60, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.rate_limit = rate_limit
        self.rate_limit_remaining = None
        self.rate_limit_reset = None

    def handle_request(self, request):
        if self.rate_limit_remaining is not None and self.rate_limit_remaining <= 0:
            sleep_time = self.rate_limit_reset - time.time()
            if sleep_time > 0:
                time.sleep(sleep_time)

        time_ = time.time()
        response = super().handle_request(request)
        
        # print(f"Request took {time.time() - time_:.2f} seconds")    
        if response.status_code == 200:
            self.rate_limit_remaining = int(response.headers.get("x-ratelimit-remaining", 0))
            self.rate_limit_reset = int(response.headers.get("x-ratelimit-reset", 0))
            return response
        elif response.status_code == 429:
            sleep_time = int(response.headers.get("x-ratelimit-reset", 60))
            if sleep_time == 0:
                sleep_time = 3
            print(f"Rate limited for {sleep_time} with key {request.headers['Authorization']}. Waiting for reset...")
            time.sleep(sleep_time)
            return self.handle_request(request)
        else:
            response.read()
            raise Exception(f"HTTP error {response.status_code}. {response.text}")


  
        