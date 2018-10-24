from skylines.schemas import FlightSchema


def test_deserialization_passes_for_valid_model_id():
    data = FlightSchema(partial=True).load(dict(modelId=4)).data
    assert data["model_id"] == 4


def test_deserialization_passes_for_missing_model_id():
    data = FlightSchema(partial=True).load(dict()).data
    assert "model_id" not in data


def test_deserialization_passes_for_null_model_id():
    data = FlightSchema(partial=True).load(dict(modelId=None)).data
    assert data["model_id"] == None
