# HistologyReagentModel

A reagent used in a histology wash

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | [optional] 
**source** | **str** |  | [optional] 
**lot_number** | **str** |  | [optional] 

## Example

```python
from aind_dataverse_service_async_client.models.histology_reagent_model import HistologyReagentModel

# TODO update the JSON string below
json = "{}"
# create an instance of HistologyReagentModel from a JSON string
histology_reagent_model_instance = HistologyReagentModel.from_json(json)
# print the JSON string representation of the object
print(HistologyReagentModel.to_json())

# convert the object into a dict
histology_reagent_model_dict = histology_reagent_model_instance.to_dict()
# create an instance of HistologyReagentModel from a dict
histology_reagent_model_from_dict = HistologyReagentModel.from_dict(histology_reagent_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


