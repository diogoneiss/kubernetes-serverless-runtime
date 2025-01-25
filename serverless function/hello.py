import json
from pprint import pprint
import redis

from mymodule import handler

if __name__ == "__main__":
    # Example usage of the handler function:
    # In practice, the serverless framework would invoke handler(event, context).

    r = redis.Redis(host='localhost', port=6379, db=0)

    METRICS_KEY = "metrics"
    dict_data = r.get(METRICS_KEY)
    if not dict_data:
        print(f"No data found for key: {METRICS_KEY}")
        raise ValueError(f"No data found for key: {METRICS_KEY}")

    dict_data = json.loads(dict_data)


    class ContextMock:
        # Simulates the context object with an 'env' field for persistence.
        def __init__(self):
            self.env = {}


    mock_context = ContextMock()
    result = handler(dict_data, mock_context)

