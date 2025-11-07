# Lima Mudlib: Game Systems Executive Summary & Customization Guide

**Version**: Based on Lima Mudlib Analysis  
**Date**: 2025-11-07

---

## Table of Contents
1. [Overview](#overview)
2. [Architecture & Modularity](#architecture--modularity)
3. [Core Game Systems](#core-game-systems)
4. [Customization Granularity Analysis](#customization-granularity-analysis)
5. [Implementation Difficulty Assessment](#implementation-difficulty-assessment)
6. [Customization Recommendations](#customization-recommendations)

---

## Overview

**Lima Mudlib** is a highly modular, modern LPC-based mudlib designed with exceptional extensibility and customization in mind. It emphasizes:

- **Natural language command parsing** (Zork-like interaction)
- **Distributed architecture** with daemon-based central systems
- **Modular inheritance structure** using multiple inheritance for composition
- **Granular control** over nearly every game system
- **Skill-based progression** with hierarchical skill trees
- **Combat event system** supporting complex interactions
- **Property-driven development** for flexible attribute handling

### Key Strengths for Customization
- Extremely clear separation of concerns
- Daemon-based systems allow swapping implementations
- Extensive use of hooks for intercepting behavior
- Configuration-driven feature toggles
- Class-based data structures for complex objects

---

## Architecture & Modularity

### Directory Structure

```
/lib
├── /std                    # Standard library base objects
│   ├── /adversary         # Combat system (monsters/NPCs)
│   ├── /body              # Player character mechanics
│   ├── /classes           # Data classes and structures
│   ├── /modules           # Behavioral modules (skills, state, etc.)
│   ├── /object            # Core object properties/behaviors
│   ├── /race              # Race definitions
│   ├── /room              # Room types and properties
│   └── [*.c]              # Base object types (weapons, armor, etc.)
├── /daemons               # Central game systems (spell_d, skill_d, guild_d, etc.)
├── /include               # Configuration headers and defines
├── /domains               # Domain-specific content
├── /cmds                  # Commands (player, wizard, creation)
├── /obj                   # Game objects
├── /secure                # Security layer
└── /data                  # Persistent data
```

### Inheritance Model

The mudlib uses **multiple inheritance** extensively:

```c
// Example: Weapon
inherit OBJ;                 // Base object
inherit M_DAMAGE_SOURCE;     // Can deal damage
inherit M_WIELDABLE;         // Can be wielded
inherit M_GETTABLE;          // Can be picked up
inherit M_MESSAGES;          // Display messages
```

**Key Principle**: Functionality is delivered through small, focused modules (prefixed with `M_`) that can be mixed and matched, providing true modular composition.

---

## Core Game Systems

### 1. COMBAT SYSTEM

**Granularity Level: VERY HIGH**

#### Architecture
- **Location**: `/lib/std/adversary/` (monsters/NPCs)
- **Core Files**: `main.c`, `condition.c`, behaviors.c`
- **Implementation**: Event-based damage application

#### Key Components

**1.1 Attack Resolution**
```c
// From adversary/main.c
take_a_swing(object target)
  ├─ Calculate hit chance
  ├─ Random roll vs. chance
  ├─ Resolve: hit/miss/disarm
  └─ Apply damage via add_event()
```

**Customization Points**:
- `chance_to_hit(weapon, target)` - Hit formula
- `disarm_chance(target)` - Disarm chance calculation
- `calculate_damage(weapon, target)` - Damage formula
- `query_attack_speed()` - Number of attacks per round
- `panic()` - Behavior when badly wounded
- `conditions` - Stun/sleep/knockout mechanics

**1.2 Combat Conditions**
```c
// From adversary/condition.c
- Stunned (time-based incapacity)
- Asleep/Knocked Out (with wake-up chances)
- Attack Speed modifiers
- Readied weapon/ammunition system
```

**1.3 Damage Type System**
- Registered via `DAMAGE_D` daemon
- Supports multiple damage types: "magic", "physical", "fire", etc.
- Weapons and armor reference these types
- **Easy to extend**: Register new damage types and create resistances

#### Combat Hooks
```c
call_hooks("prevent_combat", ...) // Intercept combat initiation
```

#### Customization Difficulty: **EASY**
- Combat formulas are straightforward functions
- Damage is event-based and traceable
- Condition system is simple state machine
- **To customize**: Override base functions or hook into event system

---

### 2. SKILLS SYSTEM

**Granularity Level: VERY HIGH**

#### Architecture
- **Location**: `/lib/std/body/skills.c` (player skills)
- **Daemon**: `/lib/daemons/skill_d.c` (skill registry)
- **Configuration**: `/lib/include/skills.h`

#### Design Philosophy: Hierarchical Skill Trees

Skills are organized as slash-separated trees:
```
combat
├── combat/melee
│   ├── combat/melee/swords
│   ├── combat/melee/axes
│   └── combat/melee/polearms
└── combat/ranged
    ├── combat/ranged/bows
    └── combat/ranged/thrown
```

**Key Mechanics**:

1. **Skill Values** (0-10,000 max)
   - Aggregated from parent skills
   - Parent skills contribute 1/AGGREGATION_FACTOR^i
   - Example: `combat/melee/swords` aggregates:
     - Own value + (combat/melee)/3 + (combat)/9

2. **Learning Curve** (Polynomial acceleration)
   ```
   Low skill    → Rapid growth (easy to learn)
   Mid skill    → Massive growth (peak efficiency)
   High skill   → Slow growth (hard to master)
   ```
   - Controlled by `LEARNING_FACTOR` (divides new learning by 1/N at skill extremes)

3. **Training Points** (Optional formal training)
   - Earned alongside skill use (1/TRAINING_FACTOR ratio)
   - Can be applied to any skill in tree
   - Represents potential improvement

#### Configuration (skills.h)
```c
#define MAX_SKILL_VALUE         10000    // Cap per skill
#define LEARNING_FACTOR         10       // End-point difficulty
#define TRAINING_FACTOR         10       // TP generation rate
#define PROPAGATION_FACTOR      2        // Parent skill contribution
#define AGGREGATION_FACTOR      3        // Combine parent scores
#define SKILL_ON_FAILURE        1        // Learn on failure
#define SKILL_MIN_ON_WIN        2        // Min learn on success
#define SKILL_MAX_ON_WIN        20       // Max learn on success
```

#### Skill Testing
```c
int test_skill(string skill, int opposing_skill)
  → Automatic learning based on:
    - Win/loss outcome
    - Opponent skill level ratio
    - Curve adjustment
```

#### Customization Points
- **Modify curves**: Change `LEARNING_FACTOR`, `PROPAGATION_FACTOR`
- **Add skill trees**: Register via `SKILL_D->register_skill("new/skill/tree")`
- **Custom learning**: Override `learn_skill()` or `test_skill()`
- **Alternative systems**: Skills are class-based data, can be replaced entirely

#### Customization Difficulty: **MODERATE**
- **Changing parameters**: TRIVIAL (edit config file)
- **Adding skills**: EASY (register with daemon)
- **Custom learning mechanics**: MODERATE (need to override core functions)
- **Complete replacement**: HARD (requires rewriting aggregation/propagation)

---

### 3. MAGIC/SPELLS SYSTEM

**Granularity Level: HIGH**

#### Architecture
- **Base Classes**: `/lib/std/spell.c`, `/lib/std/combat_spell.c`
- **Daemon**: `/lib/daemons/spell_d.c` (spell registry)
- **Framework**: Spell directories registered with daemon

#### Spell Framework

**3.1 Basic Spell Structure**
```c
inherit SPELL;  // or COMBAT_SPELL for damage

void setup()
{
    set_spell_name("Magic Missile");  // Spell name for casting
}

// Three validation gates:
mixed valid_target(object target)     // Is target valid?
mixed valid_reagent(object reagent)   // Is reagent valid?
mixed valid_circumstances(...)        // Environmental conditions?

// Actual spell effect:
protected void cast_spell(object target, object reagent)
{
    // Spell logic here
}
```

**3.2 Combat Spells**
```c
inherit COMBAT_SPELL;

void do_spell_damage(object target, function damage_func)
{
    this_body()->start_fight(target);
    this_body()->add_event(target, this_object(), 0,
                          evaluate(damage_func));
}
```

**3.3 Spell Registration**
- Spells self-register via `get_spell_name()` method
- Daemon scans spell directories and builds spell table
- Multiple spell directories supported
- Can be enabled/disabled per mud easily

#### Magic Components System
- **Reagents**: Optional spell components (validate via `valid_reagent()`)
- **Targets**: Optional spell targets (validate via `valid_target()`)
- **Circumstances**: Environmental conditions (time, location, etc.)

#### Customization Points
- **New spell types**: Create new base classes inheriting SPELL
- **Validation logic**: Override validation methods
- **Component requirements**: Add cost/requirement systems
- **Damage formulas**: Use `damage_func` callbacks
- **Spell learning**: Integrate with skill system

#### Customization Difficulty: **EASY**
- **Creating new spells**: TRIVIAL (create .c file, inherit SPELL, implement `cast_spell()`)
- **Adding spell types**: EASY (new base class)
- **Spell costs/requirements**: MODERATE (add validation methods)
- **Magic schools/types**: MODERATE (organize directories, create categorization daemon)

---

### 4. CHARACTER PROGRESSION & STATS

**Granularity Level: HIGH**

#### Architecture
- **Location**: `/lib/std/body/` (player body)
- **Stat System**: Optional (`#define USE_STATS` in config.h)
- **Race bonuses**: `/lib/std/race.c` base

#### Stat System

**4.1 Base Stats** (if `USE_STATS` enabled)
- **Strength (STR)**: Physical power
- **Agility (AGI)**: Speed and coordination
- **Intelligence (INT)**: Mental acuity
- **Wisdom (WIS)**: Perception and insight
- **Constitution (CON)**: Endurance and health
- **Charisma (CHA)**: Social influence

**4.2 Derived Stats**
Generated from base stats via transformation matrix:
```c
// Example matrix (from race.c):
CON→STR:      20%  CON→AGI:     20%  CON→WIL:     60%
WIS→STR:      7%   WIS→AGI:     7%   WIS→INT:     31%
WIS→WIL:      25%  WIS→SKILL:   30%
CHA→STR:      15%  CHA→AGI:     10%  CHA→INT:     25%
CHA→WIL:      25%  CHA→SKILL:   25%
```

**Customization**: Each race can override `query_transformation_matrix()` and `query_constant_vector()` for racial bonuses.

**4.3 Race System**
- Optional (`#define USE_RACES` in config.h)
- Built-in races: Human, Elf, Orc, Troll
- Customization: Create new race inheriting `/lib/std/race.c`

#### Character Progression Paths
1. **Skill-based**: Improve through use (automatic with `test_skill()`)
2. **Training-based**: Allocate training points to new skills
3. **Class-based**: Optional class system (defined but optional)
4. **Achievement-based**: Quest completion and milestones

#### Customization Points
- **Stats formula**: Override transformation matrix
- **Stat caps**: Modify via inheritance
- **New derived stats**: Add calculations in race class
- **Progression gates**: Add level requirements or gating
- **Experience alternative**: Replace with custom progression daemon

#### Customization Difficulty: **MODERATE**
- **Tweaking stat formulas**: EASY (modify transformation matrix)
- **Adding new stats**: MODERATE (requires class definition + calculations)
- **Alternative progression**: MODERATE (create custom daemon)
- **Full stat replacement**: HARD (requires significant rewrite)

---

### 5. CRAFTING/CREATION SYSTEM

**Granularity Level: MODERATE**

#### Architecture
- **Location**: `/lib/cmds/create/` (builder commands)
- **Commands**: `newroom.c`, `addexit.c`, `describeroom.c`, `setbrief.c`
- **No built-in crafting**: Sistema supports **player crafting of objects but no system in place**

#### Current State
The mudlib provides:
- **Room creation tools** for builders
- **Object framework** that supports crafting
- **Container system** with flexible relationships
- **Property system** for extensible attributes

#### Crafting Implementation Options

**Option A: Skill-Based Crafting**
```c
// Create custom crafting commands leveraging skill system
// Use test_skill() to determine success
// Check player inventory for materials
// Create object on success
```

**Option B: Daemon-Driven Crafting**
```c
// Create /daemons/craft_d to manage:
// - Recipes registration
// - Material validation
// - Success formulas
// - XP/skill gain
```

**Option C: Object-Based Crafting**
```c
// Inherit from base crafting object
// Each craftable item defines:
// - Required materials
// - Skills needed
// - Time to craft
// - Success chance
```

#### Key Support Systems
- **Object Templates**: Base objects support properties and attributes
- **Containers**: Can store materials with capacity management
- **Property System**: Key-value pairs for tracking crafting state
- **Hooks**: `call_hooks()` for intercepting object creation

#### Customization Difficulty: **MODERATE-HARD**
- **Simple crafting**: MODERATE (create command or object type)
- **Advanced recipes**: HARD (need daemon management system)
- **Integration with skills**: MODERATE (use `test_skill()`)
- **Persistent crafting**: HARD (requires state management)

---

### 6. GUILDS & FACTIONS SYSTEM

**Granularity Level: HIGH**

#### Architecture
- **Daemon**: `/lib/daemons/guild_d.c`
- **Framework**: Class-based guild definitions

#### Guild Features
```c
class guild_defn {
    string        guild_prospectus;      // Description
    int           guild_begone;          // What happens on leave
    int           guild_suspend_level;   // Suspension access level
    string array  guild_attributes;      // Guild abilities
    string array  guild_exclusive;       // Exclusive to guild
    string array  guild_allies;          // Allied guilds
    string array  guild_prereq;          // Required guild membership
    string array  guild_banned;          // Banned guilds
    string        guild_title;           // Formal title
    int           guild_sees_secret;     // Can see other guilds
    int           guild_is_secret;       // Attributes are secret
    int           guild_need_all;        // Need ALL prerequisites
}
```

#### Guild System Features
- **Guild hierarchies**: Prerequisites and bans
- **Attributes/Skills**: Guild-specific abilities
- **Secret guilds**: Hidden guild attributes
- **Suspension**: Players can be suspended
- **Multi-guild**: Players can join multiple guilds (with prereqs)

#### Customization Points
- **Add guild attributes**: Via `set_guild_attributes()`
- **Ally system**: Complex relationships
- **Custom suspension**: Override suspension mechanics
- **Ranking within guild**: Extend `guild_defn` class
- **Guild leadership**: Add admin tier to guild class

#### Customization Difficulty: **EASY-MODERATE**
- **Create new guilds**: TRIVIAL (call daemon functions)
- **Modify attributes**: EASY (edit guild_defn)
- **Custom membership logic**: MODERATE (override body's guild methods)
- **Ranking system**: MODERATE-HARD (requires extending class structure)

---

### 7. EQUIPMENT & INVENTORY SYSTEM

**Granularity Level: VERY HIGH**

#### Body Slot System
- **Location**: `/lib/include/bodyslots.h`
- **Standard slots**: HEAD, TORSO, ARMS, HANDS, LEGS, FEET
- **Customizable**: Add/remove slots via configuration

#### Equipment Types
```c
inherit M_WIELDABLE;      // Can be wielded (weapons)
inherit M_WEARABLE;       // Can be worn (armor)
inherit M_GETTABLE;       // Can be picked up
inherit M_MOUNTABLE;      // Can be mounted (horses, flying carpets)
```

#### Armor System
- **Multiple slots** support (wear armor on head, torso, etc.)
- **Damage types** - Different armor resists different damage
- **Weight/Size** impact mobility
- **Attributes** - Display (open), (wielded), (providing light), etc.

#### Weapon System
- **Melee weapons**: Damage calculation, hit chance modifiers
- **Ranged weapons**: Ammunition loading system
- **Loadable weapons**: Bows need ammunition to fire
- **Ammunition tracking**: "Ready" system for loaded ammo
- **Discharge system**: Weapons call `discharge()` on use

#### Container System
- **Relations**: Objects can be "in", "on", "under", "behind", etc.
- **Capacity**: Per-relation capacity limits
- **Hidden contents**: Can hide contents from view
- **Automatic reset**: Can reset contents periodically
- **Nested containers**: Full containment support

#### Customization Points
- **New body slots**: Modify `bodyslots.h`
- **Custom armor types**: Create new armor classes
- **Weapon modifications**: Create weapon base classes
- **Container types**: Derive new container variants
- **Equip restrictions**: Override validity checks

#### Customization Difficulty: **EASY-MODERATE**
- **Add body slots**: EASY (edit .h file)
- **New armor type**: EASY (create inheriting ARMOR)
- **New weapon type**: EASY (create inheriting WEAPON)
- **Custom equip logic**: MODERATE (override validity functions)
- **Complete overhaul**: MODERATE (requires careful inheritance management)

---

### 8. NPC & MONSTER SYSTEM

**Granularity Level: VERY HIGH**

#### Base Classes
- **MONSTER**: Base class for combat-capable NPCs
- **LIVING**: Non-combat living things
- **AGGRESSIVE_MONSTER**: Attacks on sight
- **WANDERING_MONSTER**: Moves between rooms
- **FOLLOWING_MONSTER**: Follows targets
- **MOVING_MONSTER**: Generic movement

#### Monster Behavior System
```c
// From adversary/behaviors.c
panic()                  // When badly wounded
flee()                   // Run away (override for AI)
surrender()              // Give up (override for AI)
target_is_asleep()       // Target unconscious behavior
```

#### Monster AI Hooks
- **Behavioral overrides**: Each method customizable
- **State machine**: Check condition before acting
- **Combat decisions**: `dispatch_opponent()` for attacking
- **Movement**: `do_move_away()` for pathfinding

#### Monster Customization
```c
// Create custom monster:
inherit MONSTER;

void setup() {
    set_name("goblin");
    set_short("a sneering goblin");
    set_long("A green-skinned creature...");
    set_skill("combat/melee", 100);
    set_hp(20);
}

void panic() {
    // Custom panic behavior
    flee();
}
```

#### Customization Points
- **Combat tactics**: Override panic/flee/surrender
- **Special abilities**: Add via inherit modules (M_*)
- **Equipment**: Set starting weapons/armor
- **Skills**: Assign combat skills
- **Loot**: Override drop() for treasure
- **Dialogue**: Add conversational triggers

#### Customization Difficulty: **EASY**
- **Basic monster**: TRIVIAL (inherit, setup method)
- **Combat AI**: EASY (override behavior methods)
- **Complex AI**: MODERATE (state machine via properties)
- **Dialogue system**: MODERATE (requires interaction handler)

---

## Customization Granularity Analysis

### Summary Matrix

| System | Granularity | Difficulty | Extensibility | Notes |
|--------|-------------|-----------|----------------|-------|
| **Combat** | Very High | Easy | Excellent | Event-based, highly hackable |
| **Skills** | Very High | Easy-Moderate | Excellent | Tree-based, configurable curves |
| **Magic** | High | Easy | Very Good | Spell class framework |
| **Stats** | High | Moderate | Very Good | Transformation matrix system |
| **Crafting** | Moderate | Moderate-Hard | Good | Need custom implementation |
| **Guilds** | High | Easy-Moderate | Very Good | Daemon-driven |
| **Equipment** | Very High | Easy-Moderate | Excellent | Modular inheritance |
| **Monsters** | Very High | Easy | Excellent | Behavior-based AI |
| **Quests** | High | Moderate | Very Good | Daemon registry + skill tests |
| **Races** | High | Easy | Very Good | Stat transformation override |

---

## Implementation Difficulty Assessment

### By Complexity Level

#### **TRIVIAL** (< 1 hour implementation)
- Add new spells
- Create basic monsters
- Add/modify body slots
- Create new weapon/armor type
- Add guild definitions
- Register new skills
- Add damage types

#### **EASY** (1-4 hours)
- Create custom crafting system (basic)
- Modify combat formulas
- Implement NPC dialogue
- Add skill learning modifications
- Create new race
- Implement custom equipment restrictions

#### **MODERATE** (4-12 hours)
- Advanced crafting system with recipes
- Complete skill learning overhaul
- Magic school system
- Guild ranking tiers
- Custom progression system
- Complex NPC AI with state machine
- Custom quest framework

#### **HARD** (12-40 hours)
- Complete stat system replacement
- Alternative combat system
- Major hook system integration
- Character class system overhaul
- Multi-skill combination system
- PvP-specific mechanics
- Balancing pass on all systems

#### **VERY HARD** (40+ hours)
- Complete mudlib architecture redesign
- Paradigm shift from skill-based to level-based
- Complete magic system replacement
- Full combat engine rewrite
- Persistence layer redesign

---

## Customization Recommendations

### For Implementing Custom Concepts

#### Concept: Level-Based Progression (instead of skill-based)
**Difficulty**: HARD  
**Approach**:
1. Disable `USE_SKILLS` in config.h
2. Create custom `/daemons/level_d.c`
3. Track experience per player
4. Cap ability scaling to level
5. Override body's progression methods
6. Integrate with combat formulas

**Time**: 20-30 hours

---

#### Concept: Magic Schools (Pyromancy, Cryomancy, etc.)
**Difficulty**: MODERATE  
**Approach**:
1. Organize spells by directory (`/spells/pyromancy/`, etc.)
2. Register spell directories with SPELL_D
3. Track "school affinity" per player (as skill or property)
4. Add cost/requirement validation based on school
5. Create school-specific base classes
6. Integrate with skill system for school advancement

**Time**: 6-12 hours

---

#### Concept: Item Crafting/Enchanting
**Difficulty**: MODERATE-HARD  
**Approach**:
1. Create `/daemons/craft_d` to manage recipes
2. Define recipe class structure
3. Add craftable object template
4. Create crafting command handler
5. Integrate skill checks using `test_skill()`
6. Handle material consumption
7. Track crafted item properties/quality

**Time**: 12-18 hours

---

#### Concept: PvP Combat Balance
**Difficulty**: MODERATE  
**Approach**:
1. Study current combat formulas (in adversary/main.c)
2. Identify damage scaling vs. player level/skill
3. Add PvP-specific damage modifiers
4. Create balanced formula set
5. Test extensively with multiple character builds
6. Add console commands for formula tweaking

**Time**: 16-24 hours

---

#### Concept: Faction/Reputation System
**Difficulty**: MODERATE  
**Approach**:
1. Extend guild_d or create `/daemons/faction_d`
2. Define faction class with reputation tracking
3. Add reputation gain/loss methods
4. Hook combat/quest events to adjust reputation
5. Gate NPC interactions behind reputation thresholds
6. Add faction-based quest rewards
7. Create faction rivalry mechanics

**Time**: 10-16 hours

---

#### Concept: Custom NPC Dialogue/Quest Trees
**Difficulty**: MODERATE  
**Approach**:
1. Create dialogue node class structure
2. Build quest tree registry daemon
3. Implement NPC interaction handler
4. Add state tracking per player
5. Create dialogue command parser
6. Integrate with quest_d for completion tracking
7. Add dialogue effect triggers (gold, XP, etc.)

**Time**: 14-20 hours

---

### Best Practices for Customization

#### 1. **Use the Module System**
- Create focused modules (M_yourfeature.c)
- Inherit into objects that need functionality
- Promotes reuse and testing

#### 2. **Leverage Daemons**
- Centralize data management
- Use for registries (spells, skills, crafts)
- Query methods for state retrieval

#### 3. **Utilize Hooks**
```c
call_hooks("prevent_combat", ...) // Intercept behavior
```
- Extensible without code modification
- Allows plugins/extensions

#### 4. **Class Data Structures**
- Use for complex object definitions
- Serializable for persistence
- Clean data organization

#### 5. **Property System**
```c
set("crafting_recipe", recipe_data);  // Non-saving
set_perm("owner_id", player_id);      // Persistent
```
- Flexible attribute storage
- Avoids object bloat

#### 6. **Configuration Over Hardcoding**
- Edit `/include/config.h` for features
- Use defines for constants
- Allows easy A/B testing

---

## Conclusion

**Lima Mudlib is exceptionally well-suited for custom game concepts** due to:

1. **Modular Architecture**: Nearly every system can be replaced or extended independently
2. **High Granularity**: Combat, skills, magic all exposed at formula level
3. **Daemon-Driven**: Central systems are swappable
4. **Multiple Inheritance**: Composition-based design maximizes flexibility
5. **Hook System**: Intercept and modify behavior without rewriting
6. **Configuration-Driven**: Many features toggled via config.h

### Implementation Feasibility

- **Most custom concepts**: 4-20 hours of development
- **Complex systems**: 20-40 hours of development
- **Paradigm shifts**: 40+ hours (generally not recommended without architecture redesign)

### Recommended Approach for New Developers

1. **Start small**: Create custom spells, monsters, guilds
2. **Learn the patterns**: Study existing modules (M_*.c files)
3. **Build a daemon**: Create your first registry daemon
4. **Extend via hooks**: Use call_hooks() before overriding methods
5. **Document your changes**: Note what you've customized in config files
6. **Iterate**: Test extensively before expanding complexity

---

## Additional Resources

### Key Files to Study
- `/lib/std/adversary/main.c` - Combat engine
- `/lib/std/body/skills.c` - Skill progression
- `/lib/std/spell.c` - Spell framework
- `/lib/daemons/skill_d.c` - Skill registry
- `/lib/daemons/spell_d.c` - Spell registry
- `/lib/include/config.h` - Configuration options
- `/lib/include/skills.h` - Skill parameters

### Design Patterns
- **Daemon pattern**: Registry and data management
- **Module pattern**: M_*.c for composition
- **Hook pattern**: call_hooks() for interception
- **Class pattern**: Class definitions in /std/classes/
- **Property pattern**: Dynamic attribute storage

---

**End of Document**
