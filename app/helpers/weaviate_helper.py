from enum import Enum

class FilterValueTypes(Enum):
    valueString = "valueString"
    valueText = "valueText"
    valueInt = "valueInt"
    valueNumber = "valueNumber"
    valueDate = "valueDate"
    valueBoolean = "valueBoolean"
    valueGeoRange = "valueGeoRange"
