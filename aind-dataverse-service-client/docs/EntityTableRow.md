# EntityTableRow

Model of Entity Table Row

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**entityid** | **str** |  | [optional] 
**entitysetname** | **str** |  | [optional] 
**name** | **str** |  | [optional] 
**logicalname** | **str** |  | [optional] 

## Example

```python
from aind_dataverse_service_client.models.entity_table_row import EntityTableRow

# TODO update the JSON string below
json = "{}"
# create an instance of EntityTableRow from a JSON string
entity_table_row_instance = EntityTableRow.from_json(json)
# print the JSON string representation of the object
print(EntityTableRow.to_json())

# convert the object into a dict
entity_table_row_dict = entity_table_row_instance.to_dict()
# create an instance of EntityTableRow from a dict
entity_table_row_from_dict = EntityTableRow.from_dict(entity_table_row_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


