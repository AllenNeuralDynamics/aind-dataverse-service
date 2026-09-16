# FundingModel

Response model for the Funding API

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**project_name** | **str** |  | [optional] 
**subproject** | **str** |  | [optional] 
**project_code** | **str** |  | [optional] 
**funding_institution** | **str** |  | [optional] 
**grant_number** | **str** |  | [optional] 
**fundees** | **str** |  | [optional] 
**investigators** | **str** |  | [optional] 

## Example

```python
from aind_dataverse_service_client.models.funding_model import FundingModel

# TODO update the JSON string below
json = "{}"
# create an instance of FundingModel from a JSON string
funding_model_instance = FundingModel.from_json(json)
# print the JSON string representation of the object
print(FundingModel.to_json())

# convert the object into a dict
funding_model_dict = funding_model_instance.to_dict()
# create an instance of FundingModel from a dict
funding_model_from_dict = FundingModel.from_dict(funding_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


