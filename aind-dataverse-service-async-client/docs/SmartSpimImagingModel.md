# SmartSpimImagingModel

Response model for the SmartSPIM Imaging API

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**experiment_run_created_on** | **datetime** |  | [optional] 
**order_created_by** | **str** |  | [optional] 
**order_project_id** | **str** |  | [optional] 
**specimen_id** | **str** |  | [optional] 
**subject_id** | **str** |  | [optional] 
**protocol_name** | **str** |  | [optional] 
**protocol_id** | **str** |  | [optional] 
**date_performed** | **datetime** |  | [optional] 
**chamber_immersion_medium** | **str** |  | [optional] 
**sample_immersion_medium** | **str** |  | [optional] 
**chamber_refractive_index** | **str** |  | [optional] 
**sample_refractive_index** | **str** |  | [optional] 
**instrument_id** | **str** |  | [optional] 
**instrument_nickname** | **str** |  | [optional] 
**experimenter_name** | **str** |  | [optional] 
**z_direction** | **str** |  | [optional] 
**y_direction** | **str** |  | [optional] 
**x_direction** | **str** |  | [optional] 
**imaging_channels** | **List[str]** |  | [optional] 
**stitching_channels** | **str** |  | [optional] 
**ccf_registration_channels** | **str** |  | [optional] 
**cell_segmentation_channels** | **List[str]** |  | [optional] 

## Example

```python
from aind_dataverse_service_async_client.models.smart_spim_imaging_model import SmartSpimImagingModel

# TODO update the JSON string below
json = "{}"
# create an instance of SmartSpimImagingModel from a JSON string
smart_spim_imaging_model_instance = SmartSpimImagingModel.from_json(json)
# print the JSON string representation of the object
print(SmartSpimImagingModel.to_json())

# convert the object into a dict
smart_spim_imaging_model_dict = smart_spim_imaging_model_instance.to_dict()
# create an instance of SmartSpimImagingModel from a dict
smart_spim_imaging_model_from_dict = SmartSpimImagingModel.from_dict(smart_spim_imaging_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


