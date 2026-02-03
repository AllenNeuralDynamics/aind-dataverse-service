# aind_dataverse_service_client.DefaultApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_table**](DefaultApi.md#get_table) | **GET** /tables/{entity_set_table_name} | Get Table
[**get_table_info**](DefaultApi.md#get_table_info) | **GET** /tables | Get Table Info


# **get_table**
> List[Dict[str, object]] get_table(entity_set_table_name)

Get Table

## Table Data
Retrieve data from the specified entity set table.

### Example


```python
import aind_dataverse_service_client
from aind_dataverse_service_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = aind_dataverse_service_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with aind_dataverse_service_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = aind_dataverse_service_client.DefaultApi(api_client)
    entity_set_table_name = 'cr138_projects' # str | The entity set name of the table to fetch

    try:
        # Get Table
        api_response = api_instance.get_table(entity_set_table_name)
        print("The response of DefaultApi->get_table:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->get_table: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **entity_set_table_name** | **str**| The entity set name of the table to fetch | 

### Return type

**List[Dict[str, object]]**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_table_info**
> List[EntityTableRow] get_table_info()

Get Table Info

## Get entity table identifying information
Retrieves identifying information for tables in an environment.

### Example


```python
import aind_dataverse_service_client
from aind_dataverse_service_client.models.entity_table_row import EntityTableRow
from aind_dataverse_service_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = aind_dataverse_service_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with aind_dataverse_service_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = aind_dataverse_service_client.DefaultApi(api_client)

    try:
        # Get Table Info
        api_response = api_instance.get_table_info()
        print("The response of DefaultApi->get_table_info:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->get_table_info: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**List[EntityTableRow]**](EntityTableRow.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

