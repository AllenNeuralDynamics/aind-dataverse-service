# HistologyWashModel

A wash step in a histology procedure

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**wash_name** | **str** |  | [optional] 
**wash_type** | **str** |  | [optional] 
**start_time** | **datetime** |  | [optional] 
**end_time** | **datetime** |  | [optional] 
**modified_by** | **str** |  | [optional] 
**reagents** | [**List[HistologyReagentModel]**](HistologyReagentModel.md) |  | [optional] 

## Example

```python
from aind_dataverse_service_async_client.models.histology_wash_model import HistologyWashModel

# TODO update the JSON string below
json = "{}"
# create an instance of HistologyWashModel from a JSON string
histology_wash_model_instance = HistologyWashModel.from_json(json)
# print the JSON string representation of the object
print(HistologyWashModel.to_json())

# convert the object into a dict
histology_wash_model_dict = histology_wash_model_instance.to_dict()
# create an instance of HistologyWashModel from a dict
histology_wash_model_from_dict = HistologyWashModel.from_dict(histology_wash_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


