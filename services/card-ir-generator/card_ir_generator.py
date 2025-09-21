#!/usr/bin/env python3
"""
Karn.ai Card IR Generator Service

Converts Scryfall JSON card data into structured Intermediate Representation (IR)
format for use throughout the Karn.ai simulation system.

Phase 1 MVP: Basic card parsing and strategic tag assignment
"""

import json
import re
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path

# For future: from pydantic import BaseModel, Field
# For now using dataclasses for simplicity

@dataclass
class CardIR:
    """Data class representing a Card Intermediate Representation"""
    ir_version: str
    generated_at: str
    card_metadata: Dict[str, Any]
    parsed_abilities: List[Dict[str, Any]]
    strategic_tags: Dict[str, Any]
    format_legality: Dict[str, Any]
    gameplay_metadata: Optional[Dict[str, Any]] = None


class AbilityParser:
    """Parses card Oracle text into structured abilities (MVP implementation)"""
    
    DAMAGE_PATTERNS = [
        r"deals (\d+) damage",
        r"(\d+) damage to",
    ]
    
    COST_PATTERNS = [
        r"\{([WUBRG\d]+)\}",  # Mana costs
        r"(?i)(tap|untap)",   # Tap/untap
        r"(?i)sacrifice",     # Sacrifice
        r"(?i)discard",       # Discard
        r"(\d+) life",        # Life costs
    ]
    
    def parse_ability(self, text: str, ability_id: str) -> Dict[str, Any]:
        """
        Parse a single ability text into structured components.
        MVP implementation focuses on basic damage and targeting.
        """
        ability = {
            "ability_id": ability_id,
            "ability_type": self._classify_ability_type(text),
            "raw_text": text,
            "parsed_components": {
                "costs": self._extract_costs(text),
                "triggers": self._extract_triggers(text),
                "effects": self._extract_effects(text),
            }
        }
        return ability
    
    def _classify_ability_type(self, text: str) -> str:
        """Classify the type of ability (MVP implementation)"""
        if ":" in text:
            return "activated"
        elif any(trigger in text.lower() for trigger in ["when", "whenever", "at the beginning"]):
            return "triggered"
        elif any(keyword in text.lower() for keyword in ["flying", "trample", "haste", "vigilance"]):
            return "keyword"
        else:
            return "static"
    
    def _extract_costs(self, text: str) -> List[Dict[str, str]]:
        """Extract costs from ability text"""
        costs = []
        
        # Mana costs
        mana_matches = re.findall(r'\{([WUBRG\d]+)\}', text)
        for mana in mana_matches:
            costs.append({"type": "mana", "value": f"{{{mana}}}"})
        
        # Tap costs
        if re.search(r'(?i)\b(tap|t)\b', text):
            costs.append({"type": "tap", "value": "Tap"})
        
        return costs
    
    def _extract_triggers(self, text: str) -> List[Dict[str, str]]:
        """Extract trigger conditions"""
        triggers = []
        
        trigger_patterns = [
            (r"when .* enters", "when"),
            (r"whenever .* dies", "whenever"),
            (r"at the beginning", "at"),
        ]
        
        for pattern, timing in trigger_patterns:
            if re.search(pattern, text.lower()):
                triggers.append({
                    "condition": re.search(pattern, text.lower()).group(0),
                    "timing": timing
                })
        
        return triggers
    
    def _extract_effects(self, text: str) -> List[Dict[str, Any]]:
        """Extract effects from ability text"""
        effects = []
        
        # Damage effects
        damage_matches = re.findall(r'deals (\d+) damage to (.+?)(?:\.|$)', text.lower())
        for damage, target in damage_matches:
            effects.append({
                "type": "damage",
                "targets": [target.strip()],
                "value": int(damage)
            })
        
        return effects


class StrategicTagger:
    """Assigns strategic tags to cards based on their properties and abilities"""
    
    TAG_RULES = {
        "interaction": {
            "removal": ["deals", "damage", "destroy", "exile", "return to hand"],
            "counterspell": ["counter target"],
            "protection": ["prevent", "indestructible", "hexproof"]
        },
        "tempo": {
            "low_cost_interaction": lambda card: card["card_metadata"]["cmc"] <= 2,
            "bounce": ["return", "bounce"]
        },
        "value": {
            "card_draw": ["draw", "cards"],
            "tutoring": ["search", "library"]
        },
        "ramp": {
            "mana_acceleration": ["add mana", "lands", "mana cost"]
        }
    }
    
    def generate_tags(self, card_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate strategic tags for a card"""
        oracle_text = card_data["card_metadata"]["oracle_text"].lower()
        hierarchical_tags = []
        flattened_tags = set()
        
        # Apply tag rules
        for category, subcategories in self.TAG_RULES.items():
            for subcategory, patterns in subcategories.items():
                if callable(patterns):
                    # Lambda function rule
                    if patterns(card_data):
                        path = [category, subcategory]
                        hierarchical_tags.append({"path": path, "confidence": 0.8})
                        flattened_tags.update(path)
                else:
                    # Pattern matching rule
                    for pattern in patterns:
                        if pattern in oracle_text:
                            path = [category, subcategory]
                            hierarchical_tags.append({"path": path, "confidence": 0.9})
                            flattened_tags.update(path)
                            break
        
        # Archetype hints based on card type and cost
        archetype_hints = self._generate_archetype_hints(card_data)
        
        # Reward hints
        reward_hints = self._generate_reward_hints(card_data, oracle_text)
        
        return {
            "hierarchical_tags": hierarchical_tags,
            "flattened_tags": list(flattened_tags),
            "archetype_hints": archetype_hints,
            "reward_hints": reward_hints
        }
    
    def _generate_archetype_hints(self, card_data: Dict[str, Any]) -> List[str]:
        """Generate archetype hints based on card properties"""
        hints = []
        cmc = card_data["card_metadata"]["cmc"]
        type_line = card_data["card_metadata"]["type_line"].lower()
        
        if cmc <= 2:
            hints.append("aggro")
        if cmc >= 6:
            hints.append("control")
        if "instant" in type_line or "flash" in card_data["card_metadata"]["oracle_text"].lower():
            hints.append("tempo")
        if any(keyword in card_data["card_metadata"]["oracle_text"].lower() 
               for keyword in ["combo", "infinite", "win the game"]):
            hints.append("combo")
        
        return hints
    
    def _generate_reward_hints(self, card_data: Dict[str, Any], oracle_text: str) -> Dict[str, Any]:
        """Generate reward shaping hints"""
        type_line = card_data["card_metadata"]["type_line"].lower()
        
        return {
            "immediate_impact": "instant" in type_line or "flash" in oracle_text,
            "delayed_impact": "enchantment" in type_line or "artifact" in type_line,
            "symmetrical": "each player" in oracle_text or "all players" in oracle_text,
            "card_advantage": self._estimate_card_advantage(oracle_text)
        }
    
    def _estimate_card_advantage(self, oracle_text: str) -> int:
        """Estimate expected card advantage"""
        if "draw" in oracle_text:
            return 1
        elif "search" in oracle_text:
            return 0  # Card neutral but improves card quality
        elif "deals" in oracle_text or "damage" in oracle_text or "destroy" in oracle_text:
            return -1  # Trading for opponent's card
        return 0


class CardIRGenerator:
    """Main service class for converting Scryfall JSON to Card IR"""
    
    def __init__(self):
        self.ability_parser = AbilityParser()
        self.strategic_tagger = StrategicTagger()
    
    def convert_scryfall_to_ir(self, scryfall_data: Dict[str, Any]) -> CardIR:
        """Convert a single Scryfall card JSON to Card IR"""
        
        # Extract core metadata
        card_metadata = self._extract_metadata(scryfall_data)
        
        # Parse abilities
        parsed_abilities = self._parse_abilities(scryfall_data)
        
        # Generate strategic tags
        card_data = {"card_metadata": card_metadata, "parsed_abilities": parsed_abilities}
        strategic_tags = self.strategic_tagger.generate_tags(card_data)
        
        # Format legality
        format_legality = self._extract_legality(scryfall_data)
        
        # Gameplay metadata
        gameplay_metadata = self._extract_gameplay_metadata(scryfall_data)
        
        return CardIR(
            ir_version="1.0.0",
            generated_at=datetime.utcnow().isoformat() + "Z",
            card_metadata=card_metadata,
            parsed_abilities=parsed_abilities,
            strategic_tags=strategic_tags,
            format_legality=format_legality,
            gameplay_metadata=gameplay_metadata
        )
    
    def _extract_metadata(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract core card metadata from Scryfall data"""
        return {
            "name": data.get("name", ""),
            "oracle_id": data.get("oracle_id", ""),
            "scryfall_id": data.get("id", ""),
            "mana_cost": data.get("mana_cost", ""),
            "cmc": data.get("cmc", 0),
            "type_line": data.get("type_line", ""),
            "oracle_text": data.get("oracle_text", ""),
            "colors": data.get("colors", []),
            "color_identity": data.get("color_identity", []),
            "keywords": data.get("keywords", []),
            "power": data.get("power"),
            "toughness": data.get("toughness"),
            "loyalty": data.get("loyalty")
        }
    
    def _parse_abilities(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse card abilities from Oracle text"""
        oracle_text = data.get("oracle_text", "")
        if not oracle_text:
            return []
        
        # For MVP, treat the entire oracle text as one ability
        # Future: Split on newlines and parse each ability separately
        ability_id = f"{data.get('name', 'unknown').lower().replace(' ', '_')}_main_effect"
        
        return [self.ability_parser.parse_ability(oracle_text, ability_id)]
    
    def _extract_legality(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract format legality information"""
        legalities = data.get("legalities", {})
        type_line = data.get("type_line", "").lower()
        
        return {
            "commander": legalities.get("commander", "not_legal"),
            "can_be_commander": "legendary" in type_line and "creature" in type_line
        }
    
    def _extract_gameplay_metadata(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract gameplay-relevant metadata"""
        type_line = data.get("type_line", "").lower()
        oracle_text = data.get("oracle_text", "").lower()
        
        # Determine valid zones
        zones = ["hand"]  # All cards can be in hand
        if any(t in type_line for t in ["creature", "artifact", "enchantment", "planeswalker"]):
            zones.append("battlefield")
        zones.extend(["graveyard", "exile", "library"])
        if not any(t in type_line for t in ["instant", "sorcery"]):
            zones.append("stack")
        
        return {
            "zones": zones,
            "enters_tapped": "enters tapped" in oracle_text or "enters the battlefield tapped" in oracle_text,
            "has_abilities_in_graveyard": "graveyard" in oracle_text and ("activate" in oracle_text or ":" in oracle_text)
        }
    
    def process_file(self, input_file: Path, output_file: Path) -> None:
        """Process a single Scryfall JSON file and output Card IR"""
        with open(input_file, 'r', encoding='utf-8') as f:
            scryfall_data = json.load(f)
        
        card_ir = self.convert_scryfall_to_ir(scryfall_data)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(asdict(card_ir), f, indent=2, ensure_ascii=False)
    
    def process_batch(self, input_dir: Path, output_dir: Path) -> None:
        """Process multiple Scryfall JSON files"""
        output_dir.mkdir(parents=True, exist_ok=True)
        
        for json_file in input_dir.glob("*.json"):
            if json_file.name.startswith("sample_card_") and not json_file.name.startswith("sample_card_ir_"):
                output_file = output_dir / f"ir_{json_file.name}"
                print(f"Processing {json_file.name} -> {output_file.name}")
                self.process_file(json_file, output_file)


def main():
    """CLI entry point for the Card IR Generator"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Karn.ai Card IR Generator")
    parser.add_argument("--input", required=True, help="Input file or directory")
    parser.add_argument("--output", required=True, help="Output file or directory")
    parser.add_argument("--batch", action="store_true", help="Batch process directory")
    
    args = parser.parse_args()
    
    generator = CardIRGenerator()
    input_path = Path(args.input)
    output_path = Path(args.output)
    
    if args.batch:
        generator.process_batch(input_path, output_path)
    else:
        generator.process_file(input_path, output_path)
    
    print("✅ Card IR generation complete!")


if __name__ == "__main__":
    main()