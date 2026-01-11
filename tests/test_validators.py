"""
Shadow Watch - Validator Tests (No Database Required)

Tests the flexible validator system across multiple industries.
"""

from shadowwatch.utils.validators import (
    validate_action,
    validate_user_id,
    validate_entity_id,
    sanitize_metadata,
    get_action_weight,
    STANDARD_ACTIONS
)
import warnings


def test_custom_actions():
    """Test that custom actions work for different industries"""
    print("\n🧪 Testing custom actions...")
    
    # E-commerce
    assert validate_action("purchase") == "purchase"
    assert validate_action("add_to_cart") == "add_to_cart"
    assert validate_action("checkout") == "checkout"
    
    # Social media
    assert validate_action("like") == "like"
    assert validate_action("follow") == "follow"
    assert validate_action("share") == "share"
    
    # Gaming
    assert validate_action("equip") == "equip"
    assert validate_action("complete") == "complete"
    assert validate_action("unlock") == "unlock"
    
    # SaaS
    assert validate_action("enable") == "enable"
    assert validate_action("create") == "create"
    assert validate_action("configure") == "configure"
    
    print("   ✅ All custom actions validated successfully")


def test_standard_actions():
    """Test that standard actions still work"""
    print("\n🧪 Testing standard actions...")
    
    assert validate_action("view") == "view"
    assert validate_action("search") == "search"
    assert validate_action("alert") == "alert"
    assert validate_action("watchlist") == "watchlist"
    assert validate_action("trade") == "trade"
    
    print("   ✅ All standard actions work")


def test_action_weights():
    """Test action weight system"""
    print("\n🧪 Testing action weights...")
    
    # Standard actions
    assert get_action_weight("trade") == 10  # Highest
    assert get_action_weight("watchlist") == 8
    assert get_action_weight("alert") == 5
    assert get_action_weight("search") == 3
    assert get_action_weight("view") == 1  # Lowest
    
    # Custom actions default to 1
    assert get_action_weight("purchase") == 1
    assert get_action_weight("like") == 1
    assert get_action_weight("custom_action") == 1
    
    print("   ✅ All action weights correct")


def test_deprecated_actions():
    """Test backwards compatibility with deprecated actions"""
    print("\n🧪 Testing deprecated actions...")
    
    # Catch deprecation warnings
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        
        # Test deprecated → recommended conversion
        result = validate_action("alert_set")
        assert result == "alert"
        assert len(w) == 1
        assert "deprecated" in str(w[0].message).lower()
        
        result = validate_action("watchlist_add")
        assert result == "watchlist"
    
    print("   ✅ Deprecated actions convert correctly with warnings")


def test_flexible_entity_ids():
    """Test that entity_id doesn't force uppercase"""
    print("\n🧪 Testing flexible entity_ids...")
    
    # Should preserve case
    assert validate_entity_id("AAPL") == "AAPL"  # Finance (uppercase)
    assert validate_entity_id("bitcoin") == "bitcoin"  # Crypto (lowercase)
    assert validate_entity_id("product_12345") == "product_12345"  # E-commerce
    assert validate_entity_id("Post-789") == "Post-789"  # Social media (mixed)
    
    print("   ✅ Entity IDs preserve case correctly")


def test_user_id_validation():
    """Test user ID validation"""
    print("\n🧪 Testing user_id validation...")
    
    # Valid IDs
    assert validate_user_id(1) == 1
    assert validate_user_id(999999) == 999999
    
    # Invalid IDs should raise
    try:
        validate_user_id(0)
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "must be positive" in str(e)
    
    try:
        validate_user_id("123")  # String, not int
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "must be an integer" in str(e)
    
    print("   ✅ User ID validation works correctly")


def test_metadata_sanitization():
    """Test metadata sanitization"""
    print("\n🧪 Testing metadata sanitization...")
    
    # None becomes empty dict
    assert sanitize_metadata(None) == {}
    
    # Valid metadata passes through
    meta = {"price": 99.99, "quantity": 1}
    assert sanitize_metadata(meta) == meta
    
    # Large metadata rejected
    try:
        huge_meta = {f"key_{i}": "x" * 1000 for i in range(100)}
        sanitize_metadata(huge_meta)
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "too large" in str(e)
    
    print("   ✅ Metadata sanitization works correctly")


def test_imports():
    """Test that all imports work"""
    print("\n🧪 Testing imports...")
    
    # Should not raise
    from shadowwatch import ShadowWatch
    from shadowwatch.models import Base
    from shadowwatch.utils.validators import STANDARD_ACTIONS
    
    assert STANDARD_ACTIONS is not None
    assert "view" in STANDARD_ACTIONS
    
    print("   ✅ All imports successful")


def main():
    print("=" * 70)
    print("Shadow Watch - Validator Tests")
    print("=" * 70)
    
    test_imports()
    test_custom_actions()
    test_standard_actions()
    test_action_weights()
    test_deprecated_actions()
    test_flexible_entity_ids()
    test_user_id_validation()
    test_metadata_sanitization()
    
    print("\n" + "=" * 70)
    print("🎉 ALL VALIDATOR TESTS PASSED!")
    print("=" * 70)
    print("\n✅ Shadow Watch is ready for:")
    print("   • Fintech (stock symbols)")
    print("   • E-commerce (product IDs)")
    print("   • Gaming (character/item names)")
    print("   • Social media (post/user IDs)")
    print("   • SaaS (feature names)")
    print("\n💡 Next: Test with PostgreSQL for full integration")


if __name__ == "__main__":
    main()
