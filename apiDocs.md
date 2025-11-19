Solar Facades API
 1.0.0 
OAS 3.1
/openapi.json
API for querying, analyzing, and monitoring photovoltaic solar facades.

system


GET
/health
Health Check

Checks the health status of the service.

Returns:

Dict[str, str]: A dictionary with the status of the service.
Parameters
Try it out
No parameters

Responses
Code	Description	Links
200	
Successful Response

Media type

application/json
Controls Accept header.
Example Value
Schema
"string"
No links
facades


GET
/facades/
List Facades

Retrieves a list of all available facades with their types for an overview comparison.

HU01: View an overview of both facades to compare their current status.

Response:

JSON object with the following structure:
count (int): Number of facades returned.
facades (list): List of facade records, each containing facade details (structure depends on storage_controller implementation).
HTTP Status Codes:
200: Successful response with the list of facades.
404: No facades available.
500: Internal server error if the query fails.
Errors:

HTTPException (404): Raised if no facades are available.
HTTPException (500): Raised if an unexpected error occurs while querying facades.
Parameters
Try it out
No parameters

Responses
Code	Description	Links
200	
Successful Response

Media type

application/json
Controls Accept header.
Example Value
Schema
"string"
No links

GET
/facades/{facade_id}
Get Facade Overview

Retrieves general information and the latest measurements for a specific facade.

HU02: Select a facade to view its data individually.

Parameters:

facade_id (str): ID of the facade to retrieve data for. Required.
facade_type (Optional[str]): Filter by facade type. Valid values: 'refrigerada', 'no_refrigerada'. Default: None (no filter).
Response:

JSON object with the following structure:
facade_id (str): The ID of the facade queried.
available_types (list): List of available facade types for the specified facade ID.
current_readings (list): List of the latest measurement records for the facade (structure depends on storage_controller implementation).
HTTP Status Codes:
200: Successful response with facade data.
404: No data available for the specified facade.
500: Internal server error if the query fails.
Errors:

HTTPException (404): Raised if no data is available for the specified facade.
HTTPException (500): Raised if an unexpected error occurs while querying the facade.
Parameters
Try it out
Name	Description
facade_id *
string
(path)
facade_id
facade_type
string | (string | null)
(query)
Filter by facade type: 'refrigerada', 'no_refrigerada'

facade_type
Responses
Code	Description	Links
200	
Successful Response

Media type

application/json
Controls Accept header.
Example Value
Schema
"string"
No links
422	
Validation Error

Media type

application/json
Example Value
Schema
{
  "detail": [
    {
      "loc": [
        "string",
        0
      ],
      "msg": "string",
      "type": "string"
    }
  ]
}
No links

GET
/facades/{facade_id}/types
Get Facade Types

Retrieves the available facade types for a specific facade ID.

Parameters:

facade_id (str): ID of the facade to retrieve types for. Required.
Response:

JSON object with the following structure:
facade_id (str): The ID of the facade queried.
types (list): List of facade types (e.g., ['refrigerada', 'no_refrigerada']).
HTTP Status Codes:
200: Successful response with facade types.
404: No data available for the specified facade.
500: Internal server error if the query fails.
Errors:

HTTPException (404): Raised if no data is available for the specified facade.
HTTPException (500): Raised if an unexpected error occurs while querying facade types.
Parameters
Try it out
Name	Description
facade_id *
string
(path)
facade_id
Responses
Code	Description	Links
200	
Successful Response

Media type

application/json
Controls Accept header.
Example Value
Schema
"string"
No links
422	
Validation Error

Media type

application/json
Example Value
Schema
{
  "detail": [
    {
      "loc": [
        "string",
        0
      ],
      "msg": "string",
      "type": "string"
    }
  ]
}
No links

GET
/facades/{facade_id}/sensors
Get Facade Sensors

Retrieves the list of sensors for a specific facade, optionally filtered by facade type.

HU03: View the individual temperature of the 15 sensors in the non-refrigerated facade.

Parameters:

facade_id (str): ID of the facade to retrieve sensors for. Required.
facade_type (Optional[str]): Filter by facade type. Valid values: 'refrigerada', 'no_refrigerada'. Default: None (no filter).
Response:

JSON object with the following structure:
facade_id (str): The ID of the facade queried.
facade_type (str or null): The facade type filter applied, if any.
count (int): Number of sensors returned.
sensors (list): List of sensor names or records (structure depends on storage_controller implementation).
HTTP Status Codes:
200: Successful response with sensor list.
404: No sensors available for the specified facade.
500: Internal server error if the query fails.
Errors:

HTTPException (404): Raised if no sensors are available for the specified facade.
HTTPException (500): Raised if an unexpected error occurs while querying sensors.
Parameters
Try it out
Name	Description
facade_id *
string
(path)
facade_id
facade_type
string | (string | null)
(query)
Filter by facade type: 'refrigerada', 'no_refrigerada'

facade_type
Responses
Code	Description	Links
200	
Successful Response

Media type

application/json
Controls Accept header.
Example Value
Schema
"string"
No links
422	
Validation Error

Media type

application/json
Example Value
Schema
{
  "detail": [
    {
      "loc": [
        "string",
        0
      ],
      "msg": "string",
      "type": "string"
    }
  ]
}
No links

GET
/facades/{facade_id}/variables
Get Facade Variables

Retrieves measurements for a specific facade with optional filters for facade type, sensor, and time range.

Parameters:

facade_id (str): ID of the facade to retrieve measurements for. Required.
facade_type (Optional[str]): Filter by facade type. Valid values: 'refrigerada', 'no_refrigerada'. Default: None (no filter).
sensor (Optional[str]): Name of a specific sensor to filter measurements. Default: None (no sensor filter).
start (Optional[str]): Start date/time for the data range in ISO8601 format (e.g., '2023-01-01T00:00:00Z'). Default: None (no start date filter).
end (Optional[str]): End date/time for the data range in ISO8601 format (e.g., '2023-01-02T00:00:00Z'). Default: None (no end date filter).
limit (int): Maximum number of measurement records to return. Must be between 1 and 5000. Default: 500.
Response:

JSON object with the following structure:
facade_id (str): The ID of the facade queried.
facade_type (str or null): The facade type filter applied, if any.
sensor_filter (str or null): The sensor name filter applied, if any.
count (int): Number of measurement records returned.
measurements (list): List of measurement records (structure depends on storage_controller implementation).
HTTP Status Codes:
200: Successful response with measurement data.
500: Internal server error if the query fails.
Errors:

HTTPException (500): Raised if an unexpected error occurs while querying measurements.
Parameters
Try it out
Name	Description
facade_id *
string
(path)
facade_id
facade_type
string | (string | null)
(query)
Filter by facade type: 'refrigerada', 'no_refrigerada'

facade_type
sensor
string | (string | null)
(query)
Specific sensor to filter (optional)

sensor
start
string | (string | null)
(query)
Start date/time in ISO8601 format

start
end
string | (string | null)
(query)
End date/time in ISO8601 format

end
limit
integer
(query)
Default value : 500

500
maximum: 5000
minimum: 1
Responses
Code	Description	Links
200	
Successful Response

Media type

application/json
Controls Accept header.
Example Value
Schema
"string"
No links
422	
Validation Error

Media type

application/json
Example Value
Schema
{
  "detail": [
    {
      "loc": [
        "string",
        0
      ],
      "msg": "string",
      "type": "string"
    }
  ]
}
No links

GET
/facades/{facade_id}/latest
Get Facade Latest

Retrieves the latest measurement for each sensor of a specific facade.

Parameters:

facade_id (str): ID of the facade to retrieve latest measurements for. Required.
facade_type (Optional[str]): Filter by facade type. Valid values: 'refrigerada', 'no_refrigerada'. Default: None (no filter).
Response:

JSON object with the following structure:
facade_id (str): The ID of the facade queried.
facade_type (str or null): The facade type filter applied, if any.
latest_readings (list): List of the latest measurement records for each sensor (structure depends on storage_controller implementation).
HTTP Status Codes:
200: Successful response with latest measurements.
404: No recent data available for the specified facade.
500: Internal server error if the query fails.
Errors:

HTTPException (404): Raised if no recent data is available for the specified facade.
HTTPException (500): Raised if an unexpected error occurs while querying latest measurements.
Parameters
Try it out
Name	Description
facade_id *
string
(path)
facade_id
facade_type
string | (string | null)
(query)
Filter by facade type: 'refrigerada', 'no_refrigerada'

facade_type
Responses
Code	Description	Links
200	
Successful Response

Media type

application/json
Controls Accept header.
Example Value
Schema
"string"
No links
422	
Validation Error

Media type

application/json
Example Value
Schema
{
  "detail": [
    {
      "loc": [
        "string",
        0
      ],
      "msg": "string",
      "type": "string"
    }
  ]
}
No links

GET
/facades/{facade_id}/average
Get Facade Average

Retrieves the average values of all variables for a specific facade.

HU08: View a graph of the average temperatures for both facades. HU04: View the average temperature per panel in the non-refrigerated facade.

Parameters:

facade_id (str): ID of the facade to calculate averages for. Required.
facade_type (Optional[str]): Filter by facade type. Valid values: 'refrigerada', 'no_refrigerada'. Default: None (no filter).
Response:

JSON object with the following structure:
facade_id (str): The ID of the facade queried.
facade_type (str or null): The facade type filter applied, if any.
averages (list): List of average values for variables (structure depends on analytics_service implementation).
HTTP Status Codes:
200: Successful response with average data.
404: No data available to calculate averages.
500: Internal server error if the query fails.
Errors:

HTTPException (404): Raised if no data is available to calculate averages.
HTTPException (500): Raised if an unexpected error occurs while querying averages.
Parameters
Try it out
Name	Description
facade_id *
string
(path)
facade_id
facade_type
string | (string | null)
(query)
Filter by facade type: 'refrigerada', 'no_refrigerada'

facade_type
Responses
Code	Description	Links
200	
Successful Response

Media type

application/json
Controls Accept header.
Example Value
Schema
"string"
No links
422	
Validation Error

Media type

application/json
Example Value
Schema
{
  "detail": [
    {
      "loc": [
        "string",
        0
      ],
      "msg": "string",
      "type": "string"
    }
  ]
}
No links

GET
/facades/{facade_id}/compare
Compare Facade Types

Compares measurements for a specific sensor between refrigerated and non-refrigerated facades.

HU13: View a comparative graph of refrigerant and water temperatures in the heat exchanger. HU17: Compare performance with and without refrigeration to validate hypotheses.

Returns two arrays: one for each facade type.

Parameters:

facade_id (str): ID of the facade to compare. Required.
sensor (str): Name of the sensor to compare. Required.
start (Optional[str]): Start date/time for the data range in ISO8601 format (e.g., '2023-01-01T00:00:00Z'). Default: None (no start date filter).
end (Optional[str]): End date/time for the data range in ISO8601 format (e.g., '2023-01-02T00:00:00Z'). Default: None (no end date filter).
limit (int): Maximum number of measurement records to return. Must be between 1 and 5000. Default: 500.
Response:

JSON object with the following structure:
facade_id (str): The ID of the facade queried.
sensor (str): The name of the sensor being compared.
comparison (dict): Dictionary with two keys, 'refrigerada' and 'no_refrigerada', each containing a list of measurement records (structure depends on storage_controller implementation).
HTTP Status Codes:
200: Successful response with comparison data.
404: No data available for comparison.
500: Internal server error if the query fails.
Errors:

HTTPException (404): Raised if no data is available for comparison.
HTTPException (500): Raised if an unexpected error occurs while comparing facade types.
Parameters
Try it out
Name	Description
facade_id *
string
(path)
facade_id
sensor *
string
(query)
Name of the sensor to compare

sensor
start
string | (string | null)
(query)
Start date/time in ISO8601 format

start
end
string | (string | null)
(query)
End date/time in ISO8601 format

end
limit
integer
(query)
Default value : 500

500
maximum: 5000
minimum: 1
Responses
Code	Description	Links
200	
Successful Response

Media type

application/json
Controls Accept header.
Example Value
Schema
"string"
No links
422	
Validation Error

Media type

application/json
Example Value
Schema
{
  "detail": [
    {
      "loc": [
        "string",
        0
      ],
      "msg": "string",
      "type": "string"
    }
  ]
}
No links
sensors


GET
/sensors/all
Get All Sensors

Retrieves a list of distinct registered sensors, optionally filtered by facade type.

Parameters:

facade_type (Optional[str]): Filter by facade type. Valid values: 'refrigerada', 'no_refrigerada'. Default: None (no filter).
limit (int): Maximum number of sensors to return. Must be between 1 and 1000. Default: 100.
Response:

JSON object with the following structure:
count (int): Number of sensors returned.
facade_type (str or null): The facade type filter applied, if any.
sensors (list): List of sensor records, each containing sensor details (structure depends on analytics_service implementation).
HTTP Status Codes:
200: Successful response with sensor list.
404: No sensors available for the specified criteria.
500: Internal server error if the query fails.
Errors:

HTTPException (404): Raised if no sensors are available for the specified criteria.
HTTPException (500): Raised if an unexpected error occurs while querying sensors.
Parameters
Try it out
Name	Description
facade_type
string | (string | null)
(query)
Filter by facade type: 'refrigerada', 'no_refrigerada'

facade_type
limit
integer
(query)
Default value : 100

100
maximum: 1000
minimum: 1
Responses
Code	Description	Links
200	
Successful Response

Media type

application/json
Controls Accept header.
Example Value
Schema
"string"
No links
422	
Validation Error

Media type

application/json
Example Value
Schema
{
  "detail": [
    {
      "loc": [
        "string",
        0
      ],
      "msg": "string",
      "type": "string"
    }
  ]
}
No links

GET
/sensors/average
Get Average

Retrieves the historical average value for a specific sensor, optionally filtered by facade type.

Parameters:

sensor_name (str): Name of the sensor to calculate the average for. Required.
facade_type (Optional[str]): Filter by facade type. Valid values: 'refrigerada', 'no_refrigerada'. Default: None (no filter).
Response:

JSON object containing the sensor average (structure depends on analytics_service implementation, expected to include an 'average' key).
HTTP Status Codes:
200: Successful response with the sensor average.
404: No data available for the specified sensor.
500: Internal server error if the query fails.
Errors:

HTTPException (404): Raised if no data is available for the specified sensor.
HTTPException (500): Raised if an unexpected error occurs while querying the sensor average.
Parameters
Try it out
Name	Description
sensor_name *
string
(query)
Name of the sensor

sensor_name
facade_type
string | (string | null)
(query)
Filter by facade type: 'refrigerada', 'no_refrigerada'

facade_type
Responses
Code	Description	Links
200	
Successful Response

Media type

application/json
Controls Accept header.
Example Value
Schema
"string"
No links
422	
Validation Error

Media type

application/json
Example Value
Schema
{
  "detail": [
    {
      "loc": [
        "string",
        0
      ],
      "msg": "string",
      "type": "string"
    }
  ]
}
No links

GET
/sensors/environmental
Get Environmental Sensors

Retrieves the list of available environmental sensors.

HU05: Visualize environmental variables such as irradiance, wind speed, temperature, and ambient humidity.

Response:

JSON object with the following structure:
count (int): Number of environmental sensors.
sensors (list): List of environmental sensor names or details (defined in analytics_service.ENVIRONMENTAL_SENSORS).
HTTP Status Codes:
200: Successful response with environmental sensor list.
500: Internal server error if the query fails.
Errors:

HTTPException (500): Raised if an unexpected error occurs while retrieving environmental sensors.
Parameters
Try it out
No parameters

Responses
Code	Description	Links
200	
Successful Response

Media type

application/json
Controls Accept header.
Example Value
Schema
"string"
No links

GET
/sensors/refrigeration
Get Refrigeration Sensors

Retrieves the list of sensors associated with the refrigeration cycle.

Response:

JSON object with the following structure:
count (int): Number of refrigeration sensors.
sensors (list): List of refrigeration sensor names or details (defined in analytics_service.REFRIGERATION_SENSORS).
HTTP Status Codes:
200: Successful response with refrigeration sensor list.
500: Internal server error if the query fails.
Errors:

HTTPException (500): Raised if an unexpected error occurs while retrieving refrigeration sensors.
Parameters
Try it out
No parameters

Responses
Code	Description	Links
200	
Successful Response

Media type

application/json
Controls Accept header.
Example Value
Schema
"string"
No links
analytics


GET
/analytics/environment/{facade_id}
Get Environmental Variables

Retrieves average environmental variables such as irradiance, wind speed, ambient temperature, and humidity for a specific facade.

HU05: Visualize environmental variables including irradiance, wind speed, temperature, and ambient humidity.

Parameters:

facade_id (str): ID of the facade to retrieve environmental data for. Required.
facade_type (Optional[str]): Filter by facade type. Valid values: 'refrigerada', 'no_refrigerada'. Default: None (no filter).
Response:

JSON object with the following structure:
facade_id (str): The ID of the facade queried.
facade_type (str or null): The facade type filter applied, if any.
environmental_variables (list): List of environmental variable records, each containing details such as irradiance, wind speed, temperature, and humidity (structure depends on analytics_service implementation).
HTTP Status Codes:
200: Successful response with environmental data.
404: No environmental data available for the specified facade.
500: Internal server error if the query fails.
Errors:

HTTPException (404): Raised if no environmental data is available for the specified facade.
HTTPException (500): Raised if an unexpected error occurs while querying environmental variables.
Parameters
Try it out
Name	Description
facade_id *
string
(path)
facade_id
facade_type
string | (string | null)
(query)
Filter by facade type: 'refrigerada', 'no_refrigerada'

facade_type
Responses
Code	Description	Links
200	
Successful Response

Media type

application/json
Controls Accept header.
Example Value
Schema
"string"
No links
422	
Validation Error

Media type

application/json
Example Value
Schema
{
  "detail": [
    {
      "loc": [
        "string",
        0
      ],
      "msg": "string",
      "type": "string"
    }
  ]
}
No links

GET
/analytics/refrigeration/{facade_id}
Get Refrigeration Variables

Retrieves average historical refrigerant cycle temperatures for a specific refrigerated facade.

HU10: Monitor the refrigerant temperature at each point in the refrigeration cycle.

Only applicable to refrigerated facades.

Parameters:

facade_id (str): ID of the refrigerated facade to retrieve data for. Required.
start (Optional[str]): Start date for the data range in ISO8601 format (e.g., '2023-01-01T00:00:00Z'). Default: None (no start date filter).
end (Optional[str]): End date for the data range in ISO8601 format (e.g., '2023-01-02T00:00:00Z'). Default: None (no end date filter).
limit (int): Maximum number of records to return. Must be at least 1. Default: 500.
Response:

JSON object with the following structure:
facade_id (str): The ID of the facade queried.
facade_type (str): Always 'refrigerada' as this endpoint is specific to refrigerated facades.
refrigeration_variables (list): List of refrigeration cycle temperature records (structure depends on analytics_service implementation).
HTTP Status Codes:
200: Successful response with refrigeration data.
404: No refrigeration data available for the specified facade or time range.
500: Internal server error if the query fails.
Errors:

HTTPException (404): Raised if no refrigeration data is available for the specified facade or time range.
Parameters
Try it out
Name	Description
facade_id *
string
(path)
facade_id
start
string | (string | null)
(query)
Start date in ISO8601 format

start
end
string | (string | null)
(query)
End date in ISO8601 format

end
limit
integer
(query)
Maximum number of records to return

Default value : 500

500
minimum: 1
Responses
Code	Description	Links
200	
Successful Response

Media type

application/json
Controls Accept header.
Example Value
Schema
"string"
No links
422	
Validation Error

Media type

application/json
Example Value
Schema
{
  "detail": [
    {
      "loc": [
        "string",
        0
      ],
      "msg": "string",
      "type": "string"
    }
  ]
}
No links

GET
/analytics/compare/{facade_id}
Compare Facade Types

Compares average performance metrics (e.g., refrigerant and water temperatures) between refrigerated and non-refrigerated facades.

HU13: Visualize a comparative graph of refrigerant and water temperatures. HU17: Compare performance with and without refrigeration to validate hypotheses.

Parameters:

facade_id (str): ID of the facade to compare. Required.
sensor_name (Optional[str]): Name of a specific sensor to filter comparison data. Default: None (no sensor filter).
Response:

JSON object with the following structure:
facade_id (str): The ID of the facade queried.
sensor_filter (str or null): The sensor name filter applied, if any.
comparison (list): List of comparison records between facade types (structure depends on analytics_service implementation).
HTTP Status Codes:
200: Successful response with comparison data.
404: No comparison data available for the specified facade or sensor.
500: Internal server error if the query fails.
Errors:

HTTPException (404): Raised if no comparison data is available for the specified facade or sensor.
HTTPException (500): Raised if an unexpected error occurs while comparing facade types.
Parameters
Try it out
Name	Description
facade_id *
string
(path)
facade_id
sensor_name
string | (string | null)
(query)
Specific sensor to filter (optional)

sensor_name
Responses
Code	Description	Links
200	
Successful Response

Media type

application/json
Controls Accept header.
Example Value
Schema
"string"
No links
422	
Validation Error

Media type

application/json
Example Value
Schema
{
  "detail": [
    {
      "loc": [
        "string",
        0
      ],
      "msg": "string",
      "type": "string"
    }
  ]
}
No links

GET
/analytics/sensors
Get Sensors By Type

Retrieves a list of available sensors, optionally filtered by facade type.

Parameters:

facade_type (Optional[str]): Filter by facade type. Valid values: 'refrigerada', 'no_refrigerada'. Default: None (no filter).
limit (int): Maximum number of sensors to return. Must be between 1 and 1000. Default: 100.
Response:

JSON object with the following structure:
facade_type (str or null): The facade type filter applied, if any.
count (int): Number of sensor records returned.
sensors (list): List of sensor records, each containing sensor details (structure depends on analytics_service implementation).
HTTP Status Codes:
200: Successful response with sensor list.
500: Internal server error if the query fails.
Errors:

HTTPException (500): Raised if an unexpected error occurs while querying sensors.
Parameters
Try it out
Name	Description
facade_type
string | (string | null)
(query)
Filter by facade type: 'refrigerada', 'no_refrigerada'

facade_type
limit
integer
(query)
Maximum number of sensors to return

Default value : 100

100
maximum: 1000
minimum: 1
Responses
Code	Description	Links
200	
Successful Response

Media type

application/json
Controls Accept header.
Example Value
Schema
"string"
No links
422	
Validation Error

Media type

application/json
Example Value
Schema
{
  "detail": [
    {
      "loc": [
        "string",
        0
      ],
      "msg": "string",
      "type": "string"
    }
  ]
}
No links
realtime


GET
/realtime/facades
Get All Realtime

Retrieves real-time data for all available facades to enable comparison of their current status.

HU01: View an overview of both facades to compare their current status.

Response:

JSON object containing real-time data for all facades (structure depends on cache_controller implementation).
HTTP Status Codes:
200: Successful response with real-time facade data.
500: Internal server error if the query fails.
Errors:

HTTPException (500): Raised if an unexpected error occurs while querying real-time data for all facades.
Parameters
Try it out
No parameters

Responses
Code	Description	Links
200	
Successful Response

Media type

application/json
Controls Accept header.
Example Value
Schema
"string"
No links

GET
/realtime/facades/{facade_id}
Get Realtime Facade

Retrieves the most recent real-time data for all sensors of a specific facade.

HU02: Select a facade to view its data individually.

Parameters:

facade_id (str): ID of the facade to retrieve real-time data for. Required.
facade_type (Optional[str]): Filter by facade type. Valid values: 'refrigerada', 'no_refrigerada'. Default: None (no filter).
Response:

JSON object with real-time data (structure depends on cache_controller implementation, expected to include a 'data' key).
HTTP Status Codes:
200: Successful response with real-time facade data.
404: No real-time data available for the specified facade.
500: Internal server error if the query fails.
Errors:

HTTPException (404): Raised if no real-time data is available for the specified facade.
HTTPException (500): Raised if an unexpected error occurs while querying real-time data.
Parameters
Try it out
Name	Description
facade_id *
string
(path)
ID of the facade

facade_id
facade_type
string | (string | null)
(query)
Filter by facade type: 'refrigerada', 'no_refrigerada'

facade_type
Responses
Code	Description	Links
200	
Successful Response

Media type

application/json
Controls Accept header.
Example Value
Schema
"string"
No links
422	
Validation Error

Media type

application/json
Example Value
Schema
{
  "detail": [
    {
      "loc": [
        "string",
        0
      ],
      "msg": "string",
      "type": "string"
    }
  ]
}
No links

GET
/realtime/facades/{facade_id}/sensor/{sensor_name}
Get Realtime Sensor

Retrieves the most recent real-time value for a specific sensor of a facade.

Parameters:

facade_id (str): ID of the facade to retrieve sensor data for. Required.
sensor_name (str): Name of the sensor to retrieve data for. Required.
facade_type (Optional[str]): Filter by facade type. Valid values: 'refrigerada', 'no_refrigerada'. Default: None (no filter).
Response:

JSON object containing the sensor value (structure depends on cache_controller implementation, expected to include a 'value' key).
HTTP Status Codes:
200: Successful response with real-time sensor data.
404: No data available for the specified sensor.
500: Internal server error if the query fails.
Errors:

HTTPException (404): Raised if no data is available for the specified sensor.
HTTPException (500): Raised if an unexpected error occurs while querying sensor data.
Parameters
Try it out
Name	Description
facade_id *
string
(path)
ID of the facade

facade_id
sensor_name *
string
(path)
Name of the sensor

sensor_name
facade_type
string | (string | null)
(query)
Filter by facade type: 'refrigerada', 'no_refrigerada'

facade_type
Responses
Code	Description	Links
200	
Successful Response

Media type

application/json
Controls Accept header.
Example Value
Schema
"string"
No links
422	
Validation Error

Media type

application/json
Example Value
Schema
{
  "detail": [
    {
      "loc": [
        "string",
        0
      ],
      "msg": "string",
      "type": "string"
    }
  ]
}
No links

GET
/realtime/facades/{facade_id}/compare
Get Realtime Comparison

Compares real-time data between refrigerated and non-refrigerated facades for a specific facade ID.

HU01: View an overview of both facades to compare their current status. HU17: Compare performance with and without refrigeration to validate hypotheses.

Parameters:

facade_id (str): ID of the facade to compare. Required.
Response:

JSON object containing real-time comparison data between facade types (structure depends on cache_controller implementation).
HTTP Status Codes:
200: Successful response with comparison data.
500: Internal server error if the query fails.
Errors:

HTTPException (500): Raised if an unexpected error occurs while comparing facade types in real time.
Parameters
Try it out
Name	Description
facade_id *
string
(path)
ID of the facade

facade_id
Responses
Code	Description	Links
200	
Successful Response

Media type

application/json
Controls Accept header.
Example Value
Schema
"string"
No links
422	
Validation Error

Media type

application/json
Example Value
Schema
{
  "detail": [
    {
      "loc": [
        "string",
        0
      ],
      "msg": "string",
      "type": "string"
    }
  ]
}
No links
alerts


GET
/alerts/errors
Get Sensor Errors

Retrieves recent sensor errors (NULL or negative values) for monitoring sensor functionality.

HU20: Query the status of sensors to verify their operation. HU15: Receive automatic alerts when sensor failures are detected.

Parameters:

limit (int): Maximum number of error records to return. Must be between 1 and 1000. Default: 100.
facade_type (Optional[str]): Filter by facade type. Valid values: 'refrigerada', 'no_refrigerada'. Default: None (no filter).
hours (int): Time range in hours to consider for recent errors. Must be between 1 and 720. Default: 24.
Response:

JSON object with the following structure:
count (int): Number of error records returned.
facade_type (str or null): The facade type filter applied, if any.
time_range_hours (int): The time range in hours used for the query.
errors (list): List of error records, each containing sensor error details (structure depends on alerts_service implementation).
HTTP Status Codes:
200: Successful response with error records.
500: Internal server error if the query fails.
Errors:

HTTPException (500): Raised if an unexpected error occurs while querying sensor errors.
Parameters
Try it out
Name	Description
limit
integer
(query)
Default value : 100

100
maximum: 1000
minimum: 1
facade_type
string | (string | null)
(query)
Filter by facade type: 'refrigerada', 'no_refrigerada'

facade_type
hours
integer
(query)
Time range in hours for recent errors

Default value : 24

24
maximum: 720
minimum: 1
Responses
Code	Description	Links
200	
Successful Response

Media type

application/json
Controls Accept header.
Example Value
Schema
"string"
No links
422	
Validation Error

Media type

application/json
Example Value
Schema
{
  "detail": [
    {
      "loc": [
        "string",
        0
      ],
      "msg": "string",
      "type": "string"
    }
  ]
}
No links

GET
/alerts/anomalies
Get Anomalies

Retrieves sensor readings that deviate from expected ranges based on defined thresholds, identifying anomalous behavior.

Parameters:

facade_id (Optional[str]): ID of the facade to filter anomalies. Default: None (no filter).
facade_type (Optional[str]): Filter by facade type. Valid values: 'refrigerada', 'no_refrigerada'. Default: None (no filter).
limit (int): Maximum number of anomaly records to return. Must be between 1 and 1000. Default: 100.
hours (int): Time range in hours to consider for recent anomalies. Must be between 1 and 720. Default: 24.
Response:

JSON object with the following structure:
count (int): Number of anomaly records returned.
facade_id (str or null): The facade ID filter applied, if any.
facade_type (str or null): The facade type filter applied, if any.
time_range_hours (int): The time range in hours used for the query.
anomalies (list): List of anomaly records, each containing anomaly details (structure depends on alerts_service implementation).
HTTP Status Codes:
200: Successful response with anomaly records.
500: Internal server error if the query fails.
Errors:

HTTPException (500): Raised if an unexpected error occurs while querying anomalies.
Parameters
Try it out
Name	Description
facade_id
string | (string | null)
(query)
ID of the facade (optional)

facade_id
facade_type
string | (string | null)
(query)
Filter by facade type: 'refrigerada', 'no_refrigerada'

facade_type
limit
integer
(query)
Default value : 100

100
maximum: 1000
minimum: 1
hours
integer
(query)
Time range in hours for recent anomalies

Default value : 24

24
maximum: 720
minimum: 1
Responses
Code	Description	Links
200	
Successful Response

Media type

application/json
Controls Accept header.
Example Value
Schema
"string"
No links
422	
Validation Error

Media type

application/json
Example Value
Schema
{
  "detail": [
    {
      "loc": [
        "string",
        0
      ],
      "msg": "string",
      "type": "string"
    }
  ]
}
No links

GET
/alerts/status/{facade_id}
Get Sensors Status

Retrieves the status (active/inactive) of all sensors for a specified facade.

HU20: Query the status of sensors to verify their operation.

A sensor is considered inactive if it has not reported data within the specified time period.

Parameters:

facade_id (str): ID of the facade to check sensor status for. Required.
facade_type (Optional[str]): Filter by facade type. Valid values: 'refrigerada', 'no_refrigerada'. Default: None (no filter).
minutes (int): Time in minutes to determine if a sensor is inactive. Must be between 1 and 1440. Default: 30.
Response:

JSON object containing sensor status details (structure depends on alerts_service implementation).
HTTP Status Codes:
200: Successful response with sensor status.
500: Internal server error if the query fails.
Errors:

HTTPException (500): Raised if an unexpected error occurs while querying sensor status.
Parameters
Try it out
Name	Description
facade_id *
string
(path)
facade_id
facade_type
string | (string | null)
(query)
Filter by facade type: 'refrigerada', 'no_refrigerada'

facade_type
minutes
integer
(query)
Time in minutes to consider a sensor inactive if no data is reported

Default value : 30

30
maximum: 1440
minimum: 1
Responses
Code	Description	Links
200	
Successful Response

Media type

application/json
Controls Accept header.
Example Value
Schema
"string"
No links
422	
Validation Error

Media type

application/json
Example Value
Schema
{
  "detail": [
    {
      "loc": [
        "string",
        0
      ],
      "msg": "string",
      "type": "string"
    }
  ]
}
No links

GET
/alerts/history
Get Alerts History

Retrieves a consolidated history of all alerts (errors and anomalies) generated by the system.

HU21: View the history of alerts generated by the system. HU15: Receive automatic alerts when sensor failures are detected.

Parameters:

limit (int): Maximum number of alert records to return. Must be between 1 and 1000. Default: 100.
facade_type (Optional[str]): Filter by facade type. Valid values: 'refrigerada', 'no_refrigerada'. Default: None (no filter).
hours (int): Time range in hours for alert history. Must be between 1 and 2160. Default: 168 (1 week).
Response:

JSON object with the following structure:
count (int): Number of alert records returned.
facade_type (str or null): The facade type filter applied, if any.
time_range_hours (int): The time range in hours used for the query.
alerts (list): List of alert records, each containing alert details (structure depends on alerts_service implementation).
HTTP Status Codes:
200: Successful response with alert history.
500: Internal server error if the query fails.
Errors:

HTTPException (500): Raised if an unexpected error occurs while querying alert history.
Parameters
Try it out
Name	Description
limit
integer
(query)
Default value : 100

100
maximum: 1000
minimum: 1
facade_type
string | (string | null)
(query)
Filter by facade type: 'refrigerada', 'no_refrigerada'

facade_type
hours
integer
(query)
Time range in hours for alert history (default: 1 week)

Default value : 168

168
maximum: 2160
minimum: 1
Responses
Code	Description	Links
200	
Successful Response

Media type

application/json
Controls Accept header.
Example Value
Schema
"string"
No links
422	
Validation Error

Media type

application/json
Example Value
Schema
{
  "detail": [
    {
      "loc": [
        "string",
        0
      ],
      "msg": "string",
      "type": "string"
    }
  ]
}
No links
exports


GET
/exports/csv/facade/{facade_id}
Export Facade Csv

Exports facade data in CSV format for analysis in external tools.

HU18: Export data in CSV format for analysis in other tools.

Supports filtering by facade type, specific sensor, and time range.

Parameters:

facade_id (str): ID of the facade to export data for. Required.
facade_type (Optional[str]): Filter by facade type. Valid values: 'refrigerada', 'no_refrigerada'. Default: None (no filter).
sensor (Optional[str]): Name of a specific sensor to filter data. Default: None (no sensor filter).
start (Optional[str]): Start date for the data range in ISO8601 format (e.g., '2023-01-01T00:00:00Z'). Default: None (no start date filter).
end (Optional[str]): End date for the data range in ISO8601 format (e.g., '2023-01-02T00:00:00Z'). Default: None (no end date filter).
Response:

File: CSV file containing facade data, returned as a StreamingResponse.
File type: text/csv
Encoding: UTF-8
Content-Disposition: attachment; filename={generated_filename}
HTTP Status Codes:
200: Successful response with CSV file.
404: No data available for the specified facade, sensor, or time range.
500: Internal server error if the CSV generation fails.
Errors:

HTTPException (404): Raised if no data is available for the specified parameters.
HTTPException (500): Raised if an unexpected error occurs during CSV generation.
Parameters
Try it out
Name	Description
facade_id *
string
(path)
facade_id
facade_type
string | (string | null)
(query)
Filter by facade type: 'refrigerada', 'no_refrigerada'

facade_type
sensor
string | (string | null)
(query)
Specific sensor to filter (optional)

sensor
start
string | (string | null)
(query)
Start date in ISO8601 format

start
end
string | (string | null)
(query)
End date in ISO8601 format

end
Responses
Code	Description	Links
200	
Successful Response

Media type

application/json
Controls Accept header.
Example Value
Schema
"string"
No links
422	
Validation Error

Media type

application/json
Example Value
Schema
{
  "detail": [
    {
      "loc": [
        "string",
        0
      ],
      "msg": "string",
      "type": "string"
    }
  ]
}
No links

GET
/exports/csv/compare/{facade_id}
Export Comparison Csv

Exports a comparative CSV file containing data for a specific sensor, comparing refrigerated and non-refrigerated facades.

Parameters:

facade_id (str): ID of the facade to compare. Required.
sensor (str): Name of the sensor to compare. Required.
start (Optional[str]): Start date for the data range in ISO8601 format (e.g., '2023-01-01T00:00:00Z'). Default: None (no start date filter).
end (Optional[str]): End date for the data range in ISO8601 format (e.g., '2023-01-02T00:00:00Z'). Default: None (no end date filter).
Response:

File: CSV file containing comparative data, returned as a StreamingResponse.
File type: text/csv
Encoding: UTF-8
Content-Disposition: attachment; filename={generated_filename}
HTTP Status Codes:
200: Successful response with CSV file.
404: No data available for the specified facade, sensor, or time range.
500: Internal server error if the CSV generation fails.
Errors:

HTTPException (404): Raised if no data is available for the specified parameters.
HTTPException (500): Raised if an unexpected error occurs during CSV generation.
Parameters
Try it out
Name	Description
facade_id *
string
(path)
facade_id
sensor *
string
(query)
Sensor to compare

sensor
start
string | (string | null)
(query)
Start date in ISO8601 format

start
end
string | (string | null)
(query)
End date in ISO8601 format

end
Responses
Code	Description	Links
200	
Successful Response

Media type

application/json
Controls Accept header.
Example Value
Schema
"string"
No links
422	
Validation Error

Media type

application/json
Example Value
Schema
{
  "detail": [
    {
      "loc": [
        "string",
        0
      ],
      "msg": "string",
      "type": "string"
    }
  ]
}
No links
temperatures


GET
/temperatures/refrigerant-cycle/{facade_id}
Get Refrigerant Cycle

Retrieves temperature measurements for each point in the refrigeration cycle of a specific facade.

HU10: View the refrigerant temperature at each point in the refrigeration cycle.

The endpoint provides temperatures at the following points:

Expansion Valve
Compressor Inlet
Compressor Outlet
Condenser Outlet
Parameters:

facade_id (str): ID of the facade to retrieve refrigeration cycle data for. Required.
start (Optional[str]): Start date/time for the data range in ISO8601 format (e.g., '2023-01-01T00:00:00Z'). Default: None (no start date filter).
end (Optional[str]): End date/time for the data range in ISO8601 format (e.g., '2023-01-02T00:00:00Z'). Default: None (no end date filter).
limit (int): Maximum number of records to return. Must be between 1 and 5000. Default: 500.
Response:

JSON object containing refrigeration cycle temperature data (structure depends on temperature_service implementation, expected to include a 'cycle_points' key).
HTTP Status Codes:
200: Successful response with refrigeration cycle temperature data.
404: No refrigeration cycle data available for the specified facade or time range.
500: Internal server error if the query fails.
Errors:

HTTPException (404): Raised if no refrigeration cycle data is available for the specified parameters.
HTTPException (500): Raised if an unexpected error occurs while querying refrigeration cycle temperatures.
Parameters
Try it out
Name	Description
facade_id *
string
(path)
ID of the facade

facade_id
start
string | (string | null)
(query)
Start date/time in ISO8601 format

start
end
string | (string | null)
(query)
End date/time in ISO8601 format

end
limit
integer
(query)
Maximum number of records

Default value : 500

500
maximum: 5000
minimum: 1
Responses
Code	Description	Links
200	
Successful Response

Media type

application/json
Controls Accept header.
Example Value
Schema
"string"
No links
422	
Validation Error

Media type

application/json
Example Value
Schema
{
  "detail": [
    {
      "loc": [
        "string",
        0
      ],
      "msg": "string",
      "type": "string"
    }
  ]
}
No links

GET
/temperatures/exchanger/{facade_id}
Get Exchanger Temps

Retrieves water temperature measurements at the inlet and outlet of the heat exchanger for a specific facade.

HU12: View the water temperature at the inlet and outlet of the heat exchanger.

The endpoint provides:

Condenser water inlet temperature
Condenser water outlet temperature
Parameters:

facade_id (str): ID of the facade to retrieve exchanger data for. Required.
start (Optional[str]): Start date/time for the data range in ISO8601 format (e.g., '2023-01-01T00:00:00Z'). Default: None (no start date filter).
end (Optional[str]): End date/time for the data range in ISO8601 format (e.g., '2023-01-02T00:00:00Z'). Default: None (no end date filter).
limit (int): Maximum number of records to return. Must be between 1 and 5000. Default: 500.
Response:

JSON object containing heat exchanger temperature data (structure depends on temperature_service implementation, expected to include an 'exchanger_data' key).
HTTP Status Codes:
200: Successful response with exchanger temperature data.
404: No exchanger data available for the specified facade or time range.
500: Internal server error if the query fails.
Errors:

HTTPException (404): Raised if no exchanger data is available for the specified parameters.
HTTPException (500): Raised if an unexpected error occurs while querying exchanger temperatures.
Parameters
Try it out
Name	Description
facade_id *
string
(path)
ID of the facade

facade_id
start
string | (string | null)
(query)
Start date/time in ISO8601 format

start
end
string | (string | null)
(query)
End date/time in ISO8601 format

end
limit
integer
(query)
Maximum number of records

Default value : 500

500
maximum: 5000
minimum: 1
Responses
Code	Description	Links
200	
Successful Response

Media type

application/json
Controls Accept header.
Example Value
Schema
"string"
No links
422	
Validation Error

Media type

application/json
Example Value
Schema
{
  "detail": [
    {
      "loc": [
        "string",
        0
      ],
      "msg": "string",
      "type": "string"
    }
  ]
}
No links

GET
/temperatures/panels/{facade_id}
Get Panels Temps

Retrieves inlet and outlet temperature measurements for one or all panels of a specific facade.

If panel_id is specified (1-5), returns data for that specific panel. If None, returns data for all five panels.

Parameters:

facade_id (str): ID of the facade to retrieve panel temperatures for. Required.
panel_id (Optional[int]): ID of the specific panel (1-5). Default: None (returns data for all panels).
start (Optional[str]): Start date/time for the data range in ISO8601 format (e.g., '2023-01-01T00:00:00Z'). Default: None (no start date filter).
end (Optional[str]): End date/time for the data range in ISO8601 format (e.g., '2023-01-02T00:00:00Z'). Default: None (no end date filter).
limit (int): Maximum number of records to return. Must be between 1 and 5000. Default: 500.
Response:

JSON object containing panel temperature data (structure depends on temperature_service implementation, expected to include a 'panels' key).
HTTP Status Codes:
200: Successful response with panel temperature data.
400: Invalid panel_id (not between 1 and 5).
404: No panel data available for the specified facade or panel.
500: Internal server error if the query fails.
Errors:

HTTPException (400): Raised if panel_id is provided but is not between 1 and 5.
HTTPException (404): Raised if no panel data is available for the specified parameters.
HTTPException (500): Raised if an unexpected error occurs while querying panel temperatures.
Parameters
Try it out
Name	Description
facade_id *
string
(path)
ID of the facade

facade_id
panel_id
integer | (integer | null)
(query)
Panel ID (1-5) or None for all panels

panel_id
start
string | (string | null)
(query)
Start date/time in ISO8601 format

start
end
string | (string | null)
(query)
End date/time in ISO8601 format

end
limit
integer
(query)
Maximum number of records

Default value : 500

500
maximum: 5000
minimum: 1
Responses
Code	Description	Links
200	
Successful Response

Media type

application/json
Controls Accept header.
Example Value
Schema
"string"
No links
422	
Validation Error

Media type

application/json
Example Value
Schema
{
  "detail": [
    {
      "loc": [
        "string",
        0
      ],
      "msg": "string",
      "type": "string"
    }
  ]
}