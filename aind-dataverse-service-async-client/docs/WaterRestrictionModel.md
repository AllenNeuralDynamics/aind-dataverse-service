# WaterRestrictionModel

Response model for the Water Restriction API

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**mouse_id** | **str** |  | 
**record_name** | **str** |  | [optional] 
**active_record** | **bool** |  | [optional] 
**baseline_weight** | **str** |  | [optional] 
**last_watered_datetime** | **datetime** |  | [optional] 
**low_weight_threshold** | **str** |  | [optional] 
**target_weight** | **str** |  | [optional] 
**targeted_weight_percentage** | **str** |  | [optional] 
**water_restriction_status** | **str** |  | [optional] 
**change_date_time** | **datetime** |  | [optional] 
**new_value** | **str** |  | [optional] 
**old_value** | **str** |  | [optional] 

## Example

```python
from aind_dataverse_service_async_client.models.water_restriction_model import WaterRestrictionModel

# TODO update the JSON string below
json = "{}"
# create an instance of WaterRestrictionModel from a JSON string
water_restriction_model_instance = WaterRestrictionModel.from_json(json)
# print the JSON string representation of the object
print(WaterRestrictionModel.to_json())

# convert the object into a dict
water_restriction_model_dict = water_restriction_model_instance.to_dict()
# create an instance of WaterRestrictionModel from a dict
water_restriction_model_from_dict = WaterRestrictionModel.from_dict(water_restriction_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


