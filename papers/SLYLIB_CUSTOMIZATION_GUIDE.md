# Skylib MUD Customization Difficulty Analysis

## Overview

**Customization Difficulty: MODERATE to HIGH** - This is a mature, feature-rich codebase with deep systems, but with well-documented patterns for extending them. Most systems are modular rather than monolithic, making targeted customizations feasible.

---

## System-by-System Breakdown

### 1. SKILLS SYSTEM

**Difficulty: LOW-MODERATE**

**Architecture:**

- Hierarchical tree structure (6 main branches → sub-categories → leaf nodes)
- Main categories: Fighting, Magic, Faith, Crafts, Covert, General
- Defined in `/handlers/skills.c` via `_skills` mapping
- Each skill has associated stat bonuses (e.g., "DDDDD" = different stat dependencies)

**Customization Options:**

- ✅ Easy: Add new leaf skills (non-breaking)
- ⚠️ Moderate: Reorganize tree structure (requires cascade updates)
- ⚠️ Moderate: Change stat bonuses (math exists in skills handler, well-structured)
- ✅ Easy: Add new skill categories
- 🔴 Hard: Change core hierarchy (affects player saves, inheritance)

**Key Files:**

- `/handlers/skills.c` - Central skills registry & stat bonus mapping
- `/std/living/skills.c` - Per-character skill tracking & calculation
- `/include/tasks.h` - Task/skill check definitions

**Notes:** Skills are *not* hardcoded—they're data-driven via mappings. Adding skills is clean. However, the stat bonus system is tightly coupled; changing stat mechanics requires edits across combat/skills code.

---

### 2. COMBAT SYSTEM

**Difficulty: MODERATE**

**Architecture:**

- Multi-stage combat pipeline with hooks at each stage:
  - PREPARE_ATTACK (select weapon/attack)
  - MODIFY_ATTACK (adjust parameters)
  - MODIFY_DAMAGE (alter damage output)
  - MODIFY_MESSAGES (customize flavor text)
  - FINISH_ATTACK (final effects)
- Tactical system: attitudes (defensive→offensive), parry modes, focus targets
- Special attacks framework: tactical, melee, dodge-reactive, parry-reactive

**Customization Options:**

- ✅ Easy: Add new attack types via `add_attack()` with custom functions
- ✅ Easy: Add special attack callbacks (tactical maneuvers, etc.)
- ✅ Easy: Override `modify_damage()` per-weapon/per-creature
- ⚠️ Moderate: Add new combat stages (requires pipeline changes)
- 🔴 Hard: Replace core combat loop (deeply integrated into living.c)

**Key Files:**

- `/std/living/combat.c` - Main combat engine (250+ lines of core logic)
- `/std/weapon_logic.c` - Attack definition & execution (modular, well-designed)
- `/handlers/combat.c` - Higher-level combat coordination
- `/include/combat.h` - Combat stage defines & data classes

**Notes:** The attack system is **extensible by design**—you can define custom attacks with unique damage calculations and callbacks without touching core combat. Combat stages are defined via macros, making it possible to inject custom logic at known points.

---

### 3. MAGIC & SPELL SYSTEM

**Difficulty: MODERATE to HIGH**

**Architecture:**

- Two-tier system:
  - **Spells**: Object-oriented (`/spells` directory), each spell is an object with setup logic
  - **Rituals**: Multi-stage system (similar to spells but with deity bindings)
- Spells defined via `#define` data structures in spell objects
- Spell stages with macros: `STAGE()`, `SKILL()`, `DIFF()`, `MESSAGES()`, `FAIL_MESSAGES()`
- Magic handler (`/handlers/magic_handler.c`) manages spell execution & effects

**Customization Options:**

- ✅ Easy: Add new spells (copy existing, modify data)
- ✅ Easy: Add spell tiers (TIER_1 exists, tier system in place)
- ✅ Easy: Create spell variants (inheritance available)
- ⚠️ Moderate: Add new effect types (effects system exists but requires integration)
- ⚠️ Moderate: Custom spell stages (macro system allows it, but requires careful design)
- 🔴 Hard: Change core spell mechanics (skill requirements, targeting, message expansion)

**Key Files:**

- `/handlers/magic_handler.c` - Spell execution, effects, message expansion
- `/include/magic.h` - Spell stage macros & argument structure
- `/include/spells.h` - Spell definition constants
- `/std/living/spells.c` - Per-character spell tracking

**Issues to Watch:**

- Spells lost on death (by design—philosophical choice)
- Message expansion system is non-trivial (see `expand_spell_message()`)
- Ritual system tightly coupled to deity handler

**Recommendation:** Easier to extend with new spells/rituals than to modify existing mechanics. The macro-based stage system is clever but opaque for beginners.

---

### 4. WEAPONS SYSTEM

**Difficulty: LOW to MODERATE**

**Architecture:**

- Weapons inherit from standard objects with attack definitions
- Attack data stored as arrays: `[chance, damage, type, skill, function]`
- Damage calculation via dice notation: `fixed + MdN`
- Attack messages customizable per attack type (blunt, pierce, etc.)
- Weapon types are inferred from attack skills

**Customization Options:**

- ✅ Easy: Create new weapon archetypes (inherit + define attacks)
- ✅ Easy: Add attack messages via `add_attack_message()`
- ✅ Easy: Create special weapon functions with damage callbacks
- ✅ Easy: Add weapon-specific status displays
- ⚠️ Moderate: Create weapon enchantment systems (framework exists via effects)
- 🔴 Hard: Change damage calculation logic (math baked into core)

**Key Files:**

- `/std/weapon_logic.c` - Attack definition & execution (modular!)
- `/std/object.c` or `/obj/weapon.c` - Base weapon template
- Weapon categories in `/doc/weapons/` (swords, spears, etc.)

**Notes:** **Weapons are NOT hardcoded**—they're data-driven objects. Adding new weapon types is trivial. The attack framework is well-factored and supports custom callbacks, making weapon specialization straightforward.

---

### 5. CHARACTER STATS & ATTRIBUTES

**Difficulty: LOW**

**Architecture:**

- 5-stat system (strength, dexterity, constitution, intelligence, wisdom = SDCIW)
- Stats influence skill bonuses via stat mappings
- Stored per-character, with modification functions

**Customization Options:**

- ✅ Easy: Add new stats (requires edits to stat handler + skill mappings)
- ⚠️ Moderate: Change stat calculation formulas
- ⚠️ Moderate: Add stat-dependent features
- 🔴 Hard: Remove/rename existing stats (cascading impact)

**Key Files:**

- `/std/living/stats.c` - Stat tracking
- `/handlers/skills.c` - Stat → skill bonus mappings

---

### 6. ITEMS & INVENTORY

**Difficulty: LOW**

**Architecture:**

- Container-based inheritance chain
- Items track weight, volume, properties
- Modular attachment of behaviors (books, tools, armor, etc.)

**Customization Options:**

- ✅ Easy: Create new item types
- ✅ Easy: Add item properties/effects
- ✅ Easy: Extend carry/wear limitations
- ✅ Easy: Create scripted item behaviors

---

### 7. COMMAND SYSTEM

**Difficulty: LOW to MODERATE**

**Architecture:**

- `/handlers/command_handler` routes player input
- Player commands in `/cmds` (per-privilege level)
- Soul system for emotes/actions

**Customization Options:**

- ✅ Easy: Add new player commands (create new .c file in `/cmds`)
- ✅ Easy: Override existing commands
- ⚠️ Moderate: Add command routing logic

---

### 8. QUEST SYSTEM

**Difficulty: MODERATE**

**Architecture:**

- Quest handler (`/handlers/quest_handler.c`) manages objectives
- Quests are task-based objects with reward logic
- Tied to XP and item acquisition

**Customization Options:**

- ✅ Easy: Create new quest templates
- ✅ Easy: Add quest rewards
- ⚠️ Moderate: Create conditional quest chains
- ⚠️ Moderate: Add dynamic quest generation

---

## Customization Effort Matrix

| System   | Add New     | Modify Existing | Replace Entirely | Ease     |
| -------- | ----------- | --------------- | ---------------- | -------- |
| Skills   | Easy ✅      | Moderate ⚠️     | Hard 🔴          | Easy     |
| Combat   | Easy ✅      | Moderate ⚠️     | Hard 🔴          | Moderate |
| Spells   | Easy ✅      | Moderate ⚠️     | Hard 🔴          | Moderate |
| Weapons  | Easy ✅      | Easy ✅          | Hard 🔴          | Easy     |
| Stats    | Moderate ⚠️ | Moderate ⚠️     | Hard 🔴          | Low      |
| Items    | Easy ✅      | Easy ✅          | Easy ✅           | Easy     |
| Commands | Easy ✅      | Easy ✅          | Moderate ⚠️      | Easy     |
| Quests   | Easy ✅      | Moderate ⚠️     | Hard 🔴          | Moderate |

---

## Pain Points for Customization

### 1. **Stat Bonus System is Tightly Coupled**

Skills bonuses are hardcoded mappings in the skills handler. Adding a new stat requires:

- Update skill bonuses (hundreds of entries)
- Update combat calculations
- Update spell calculations
  **Solution:** Create a centralized stat configuration module.

### 2. **Death Mechanics**

Spells/rituals lost on death. This is by design but impacts progression systems.
**Solution:** Create a "spell resurrection" system if desired.

### 3. **Message Expansion**

The `expand_spell_message()` function is feature-rich but complex. Adding new message tokens requires careful updates.
**Solution:** Document the expansion system, create wrapper functions.

### 4. **Lack of Central Configuration**

Magic numbers scattered throughout code (e.g., XP penalties, skill costs, etc.).
**Solution:** Create a `/include/config.h` for all tunable values.

### 5. **Living.c Inheritance Chain**

Deep inheritance (living → weapon_logic → container → effects, etc.). Hard to trace all dependencies.
**Solution:** Document inheritance chain; use IDE with call hierarchy.

---

## Recommendation: Customization Roadmap

**For Light Customization (easiest path):**

1. Add new skills to the tree
2. Create new weapon types & attacks
3. Write new spells (copy existing templates)
4. Add new commands/emotes
5. Create new quest types

**For Moderate Customization:**

1. Create new combat abilities (tactical maneuvers)
2. Add spell effects & status conditions
3. Create item enchantment framework
4. Build NPC behavior systems

**For Heavy Customization:**

1. Refactor stat system (requires comprehensive updates)
2. Add new character progressions beyond skills
3. Implement alternative magic schools
4. Create dynamic encounter systems

---

## Positive Aspects (Low Customization Friction)

✅ **Data-driven** systems (skills, weapons, spells as objects/mappings, not hardcoded)
✅ **Modular design** with clear inheritance patterns
✅ **Extensive hooks** for extensions (modify_damage, add_attack, add_spell_effect, etc.)
✅ **Well-documented** code with autodoc comments
✅ **Object-oriented** architecture (each weapon/spell is an object)
✅ **Handlers** centralize logic (skills handler, magic handler, quest handler)
✅ **Framework** for testing & iteration (taskmaster system)

---

## Summary

**Skylib is customization-friendly for evolutionary changes, but requires architectural refactoring for revolutionary changes.**

- **Best for:** Building on existing systems (new skills, weapons, spells, quests)
- **Moderate for:** Extending systems with new features (combat abilities, effects)
- **Difficult for:** Wholesale system replacement or stat/core mechanic overhauls

The codebase is **mature and stable**, with clear design patterns. Most customizations can be done by adding new objects/handlers rather than modifying existing code. This is a strength for maintenance.

**Estimated effort for a moderately skilled LPC programmer:**

- Add 10 new skills: 2 hours
- Create 5 new weapons: 4 hours
- Write 3 new spells: 6 hours
- Add new quest chain: 8 hours
- **Refactor stat system:** 40+ hours (major undertaking)