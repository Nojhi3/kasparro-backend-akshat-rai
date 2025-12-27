import pytest
from datetime import datetime
from schemas.etl_schema import UnifiedRow
from pydantic import ValidationError

def test_valid_transformation():
    """Test that valid data passes Pydantic validation."""
    row = UnifiedRow(
        entity_name="Bitcoin",
        value=50000.0,
        event_timestamp=datetime.now(),
        source="test_api",
        original_id="btc"
    )
    assert row.entity_name == "Bitcoin"
    assert row.value == 50000.0

def test_negative_value_validation():
    """Test that negative prices raise an error (Pydantic Validation)."""
    with pytest.raises(ValidationError):
        UnifiedRow(
            entity_name="Bitcoin",
            value=-100.0, # Invalid!
            event_timestamp=datetime.now(),
            source="test_api",
            original_id="btc"
        )

def test_missing_field_validation():
    """Test that missing required fields raise an error."""
    with pytest.raises(ValidationError):
        # Missing 'value'
        UnifiedRow(
            entity_name="Bitcoin",
            event_timestamp=datetime.now(),
            source="test_api",
            original_id="btc"
        )