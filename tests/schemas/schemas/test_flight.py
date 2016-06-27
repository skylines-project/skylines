from skylines.schemas import FlightSchema


def test_deserialization_passes_for_valid_model_id():
    data, errors = FlightSchema(partial=True).load(dict(modelId=4))
    assert not errors
    assert data['model_id'] == 4


def test_deserialization_passes_for_missing_model_id():
    data, errors = FlightSchema(partial=True).load(dict())
    assert not errors
    assert 'model_id' not in data


def test_deserialization_passes_for_null_model_id():
    data, errors = FlightSchema(partial=True).load(dict(modelId=None))
    assert not errors
    assert data['model_id'] == None
