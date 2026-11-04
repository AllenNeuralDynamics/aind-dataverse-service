# HistologyModel

Response model for the Histology API

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**procedure_name** | **str** |  | [optional] 
**experiment_run_created_on** | **datetime** |  | [optional] 
**specimen_id** | **str** |  | [optional] 
**subject_id** | **str** |  | [optional] 
**protocol_id** | **str** |  | [optional] 
**protocol_name** | **str** |  | [optional] 
**washes** | [**List[HistologyWashModel]**](HistologyWashModel.md) |  | [optional] 

## Example

```python
from aind_dataverse_service_client.models.histology_model import HistologyModel

# TODO update the JSON string below
json = "{}"
# create an instance of HistologyModel from a JSON string
histology_model_instance = HistologyModel.from_json(json)
# print the JSON string representation of the object
print(HistologyModel.to_json())

# convert the object into a dict
histology_model_dict = histology_model_instance.to_dict()
# create an instance of HistologyModel from a dict
histology_model_from_dict = HistologyModel.from_dict(histology_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


