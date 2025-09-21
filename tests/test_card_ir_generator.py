#!/usr/bin/env python3
"""
Tests for the Card IR Generator service
"""

import json
import sys
from pathlib import Path

# Add the services directory to the path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "services" / "card-ir-generator"))

from card_ir_generator import CardIRGenerator, AbilityParser, StrategicTagger


def test_lightning_bolt_conversion():
    """Test converting Lightning Bolt from Scryfall JSON to Card IR"""
    
    # Sample Lightning Bolt data (simplified from our downloaded sample)
    lightning_bolt_data = {
        "name": "Lightning Bolt",
        "oracle_id": "4457ed35-7c10-48c8-9776-456485fdf070",
        "id": "77c6fa74-5543-42ac-9ead-0e890b188e99",
        "mana_cost": "{R}",
        "cmc": 1.0,
        "type_line": "Instant",
        "oracle_text": "Lightning Bolt deals 3 damage to any target.",
        "colors": ["R"],
        "color_identity": ["R"],
        "keywords": [],
        "legalities": {
            "commander": "legal"
        }
    }
    
    generator = CardIRGenerator()
    card_ir = generator.convert_scryfall_to_ir(lightning_bolt_data)
    
    # Basic assertions
    assert card_ir.card_metadata["name"] == "Lightning Bolt"
    assert card_ir.card_metadata["cmc"] == 1.0
    assert card_ir.format_legality["commander"] == "legal"
    assert card_ir.format_legality["can_be_commander"] == False
    
    # Check that strategic tags are generated
    assert len(card_ir.strategic_tags["flattened_tags"]) > 0
    assert "interaction" in card_ir.strategic_tags["flattened_tags"]
    
    # Check that abilities are parsed
    assert len(card_ir.parsed_abilities) > 0
    assert card_ir.parsed_abilities[0]["raw_text"] == "Lightning Bolt deals 3 damage to any target."
    
    print("✅ Lightning Bolt conversion test passed!")
    return card_ir


def test_ability_parser():
    """Test the AbilityParser class"""
    parser = AbilityParser()
    
    # Test damage parsing
    ability = parser.parse_ability("Lightning Bolt deals 3 damage to any target.", "test_ability")
    
    assert ability["ability_type"] == "static"
    assert len(ability["parsed_components"]["effects"]) == 1
    assert ability["parsed_components"]["effects"][0]["type"] == "damage"
    assert ability["parsed_components"]["effects"][0]["value"] == 3
    
    print("✅ Ability parser test passed!")


def test_strategic_tagger():
    """Test the StrategicTagger class"""
    tagger = StrategicTagger()
    
    # Sample card data
    card_data = {
        "card_metadata": {
            "cmc": 1.0,
            "type_line": "Instant",
            "oracle_text": "Lightning Bolt deals 3 damage to any target."
        }
    }
    
    tags = tagger.generate_tags(card_data)
    
    assert "interaction" in tags["flattened_tags"]
    assert "removal" in tags["flattened_tags"]
    assert "aggro" in tags["archetype_hints"]  # Low CMC instant
    assert tags["reward_hints"]["immediate_impact"] == True  # Instant
    assert tags["reward_hints"]["card_advantage"] == -1  # Damage spell
    
    print("✅ Strategic tagger test passed!")


def run_integration_test():
    """Run an integration test using our real sample data"""
    
    # Path to our sample Lightning Bolt data
    sample_file = Path(__file__).parent.parent / "data" / "sample_card_lightning_bolt.json"
    
    if not sample_file.exists():
        print("⚠️  Sample file not found, skipping integration test")
        return
    
    generator = CardIRGenerator()
    output_file = Path(__file__).parent.parent / "data" / "test_output_lightning_bolt.json"
    
    try:
        generator.process_file(sample_file, output_file)
        
        # Verify the output
        with open(output_file, 'r') as f:
            generated_ir = json.load(f)
        
        assert generated_ir["card_metadata"]["name"] == "Lightning Bolt"
        assert "strategic_tags" in generated_ir
        assert "parsed_abilities" in generated_ir
        
        print("✅ Integration test passed!")
        print(f"   Generated IR saved to: {output_file}")
        
        # Pretty print a summary of what was generated
        print(f"   Strategic tags: {generated_ir['strategic_tags']['flattened_tags']}")
        print(f"   Archetype hints: {generated_ir['strategic_tags']['archetype_hints']}")
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        raise


if __name__ == "__main__":
    print("🧪 Running Card IR Generator tests...")
    print()
    
    # Run unit tests
    test_ability_parser()
    test_strategic_tagger()
    test_lightning_bolt_conversion()
    
    # Run integration test
    run_integration_test()
    
    print()
    print("🎉 All tests passed! The Card IR Generator MVP is working.")