# Final Realms MUD - Game Systems Executive Summary & Customization Guide

**Version:** FluffOS 2.9  
**Architecture:** Modular LPC-based object system  
**Last Updated:** November 2024

---

## Table of Contents

1. [Executive Overview](#executive-overview)
2. [System Architecture](#system-architecture)
3. [Core Game Systems](#core-game-systems)
4. [Customization Guide by System](#customization-guide-by-system)
5. [Integration Points & Extensibility](#integration-points--extensibility)
6. [Difficulty Assessment](#difficulty-assessment)

---

## Executive Overview

Final Realms is a **mature, highly modular mudlib** with strong architectural separation of concerns. It uses an object-oriented inheritance model where core gameplay logic is centralized in `/lib/std` with extensible subclasses for customization.

### Key Strengths:
- **Modular Design**: Each system (combat, spells, skills, stats) is independently composed
- **Inheritance-Based**: Easy to override functionality without modifying core files
- **Multi-stat Economy**: Uses 6-stat system (STR, DEX, CON, INT, WIS, CHA) with per-class modifiers
- **Guild-Based Class System**: Flexible "guild" architecture supporting multiple playstyles
- **Role-Based Architecture**: Separates living objects (NPCs/players) from items and rooms

### Architecture Diagram (Simplified):

```
┌─────────────────────────────────────────┐
│  /std/living.c (Base Living Object)    │
├─────────────────────────────────────────┤
│ Composes (Inherits):                   │
│ ├─ alignment.c     (moral alignment)   │
│ ├─ combat.c        (attack logic)      │
│ ├─ spells.c        (spell effects)     │
│ ├─ skills.c        (skill management)  │
│ ├─ stats.c         (attributes/HP/GP)  │
│ ├─ equip.c         (equipment system)  │
│ ├─ health.c        (damage/healing)    │
│ ├─ money.c         (currency)          │
│ └─ ... (and more)                      │
└─────────────────────────────────────────┘
           ▲                    ▲
           │                    │
     ┌─────┴──────┐      ┌──────┴─────┐
     │ NPCs       │      │   Players  │
     │ (Monsters) │      │            │
     └────────────┘      └────────────┘
```

---

## System Architecture

### File Organization

```
/lib/std/
├─ living/              # Core character engine
│  ├─ living.c         # Base living object (composes everything)
│  ├─ combat.c         # Attack/defense/protection logic
│  ├─ spells.c         # Spell effect management & casting
│  ├─ skills.c         # Skill level calculation & bonuses
│  ├─ stats.c          # Attributes (STR/DEX/CON/INT/WIS/CHA)
│  ├─ health.c         # HP, GP, XP, damage tracking
│  ├─ equip.c          # Equipment management (wear/wield)
│  ├─ alignment.c      # Good/Evil/Lawful/Chaotic tracking
│  ├─ money.c          # Coin/currency system
│  └─ ... (additional subsystems)
│
├─ guilds/              # Class system implementation
│  ├─ guild.c          # Base class definition
│  ├─ fighter.c        # Warrior class example
│  ├─ mage.c           # Mage class example
│  ├─ rogue.c          # Rogue class example
│  ├─ cleric.c         # Priest class example
│  └─ priests/,wizards/  # Subguilds for specialization
│
├─ races/               # Racial system
│  ├─ base.c           # Base race definition
│  ├─ human.c          # Human race
│  ├─ elf.c            # Elf race
│  ├─ dwarf.c          # Dwarf race
│  └─ ... (16+ races total)
│
├─ spells/              # Spell system
│  ├─ examples/
│  │  ├─ base.c        # Base spell class
│  │  ├─ bless.c       # Example blessing spell
│  │  ├─ light.c       # Example light spell
│  │  └─ template.c    # Spell creation template
│  ├─ examples/SPECIALISTS  # Sphere restrictions
│  └─ examples/GP_COST_FOR_SPELLS  # Cost table
│
├─ skills.c            # Global skill system registry
├─ item.c              # Base item/equipment class
├─ weapon_logic.c      # Combat damage calculation
├─ object.c            # Base object class (ALL objects inherit)
└─ ... (containers, shops, rooms, etc.)
```

### Object Inheritance Hierarchy

```
/std/object.c (Most basic LPC object)
    ▼
/std/item.c (Wearable/holdable items)
    ├─→ /std/armour.c (Armor pieces)
    └─→ /std/weapon.c (Weapons)

/std/object.c
    ▼
/std/living.c (Everything that is alive - NPCs, Players)
    └─ Uses multiple inheritance for modular composition
```

---

## Core Game Systems

### 1. COMBAT SYSTEM

**Location:** `/lib/std/living/combat.c`, `/lib/std/weapon_logic.c`, `/lib/std/unarmed_combat.c`

#### Combat Architecture:

- **Base System:** AD&D 2nd Edition derived (modified)
- **Core Mechanic:** THAC0 (To Hit AC 0) system
  - Default dice pool: d20
  - Base AC/THAC0 scaled at 100/200 (internally precise)
  - Formula: `THAC0 - roll = AC to hit`

#### Combat Flow:

1. **Initialization**: Attacker lists maintained per living object
2. **Target Selection**: 
   - Random selection from attacker list
   - Concentration mechanic for focused attacks
   - Protection mechanics (one character can defend another)
3. **Attack Resolution**:
   - Attack bonus from weapon + attacker level
   - Defense AC from armor + DEX modifier
   - Hit determination + damage roll
4. **Damage Application**:
   - Weapon damage dice (varies by weapon type)
   - Strength/magic bonuses applied
   - Reduction by target's armor class

#### Key Variables & Functions:

```lpc
query_fighting()           // Returns combat status (0=not fighting, 1=aggressive NPC, 
                          // 2=passive NPC, 4=interactive player fighting)
query_attackee()          // Returns current target
set_concentrate(object)   // Focus attacks on specific opponent
query_dodging()           // Check if character is dodging
set_protector(object)     // Set who is protecting this character
attack_by(object)         // Called when attacked, adds to attacker list
```

#### Customization Points:

- **Modify THAC0 calculation** in `/lib/std/living/combat.c` `attack()` function
- **Change damage formula** in `/lib/std/weapon_logic.c` `apply_damage()` function
- **Add new attack types** by creating weapon subclasses with unique `weapon_attack()` implementations
- **Implement special attack mechanics** via guild-specific overrides of `query_protect_valid()` or `query_concentrate_valid()`

#### Difficulty Level: **MEDIUM**
- Core combat loop is well-abstracted but tightly integrated with stats/health
- Adding new attack types is easy; changing fundamental rules requires careful refactoring

---

### 2. CHARACTER PROGRESSION & LEVELING

**Location:** `/lib/std/living/stats.c`, `/lib/std/living/health.c`, `/lib/std/guild.c`

#### Progression Mechanics:

**Experience & Leveling:**
- Characters gain XP from combat and other activities
- XP threshold for leveling managed by guild object
- Upon level-up: HP/GP recalculated based on class and stats

**Stat System (6-Attribute):**
- **STR (Strength)**: Damage, carry capacity, melee attacks
- **DEX (Dexterity)**: AC bonus, initiative, ranged accuracy
- **CON (Constitution)**: HP pool, poison resistance
- **INT (Intelligence)**: Spell learning, magic resistance
- **WIS (Wisdom)**: Spell casting bonus, perception
- **CHA (Charisma)**: NPC reactions, charm effects, lucky rolls

**HP Calculation:**
```lpc
// Per level:
max_hp = guild->query_dice() * level + hp_bonus + charisma_modifier
// Example: Fighter (d10) at level 5: 10*5 + bonuses
```

**GP (Magic Power) Calculation:**
```lpc
// Per level based on main skill stat:
max_gp = (skill_value * level / 2) + bonuses
// skill_value = character's main stat (STR for fighters, INT for mages, etc.)
```

**Stat Modifications:**
- Base stats from race (e.g., elves get +1 DEX, -1 CON)
- Temporary bonuses from potions/items
- Permanent bonuses from guild leveling

#### Key Functions:

```lpc
recalc_stats(int levels)       // Recalculate HP/GP on level gain
reset_carry_cap()              // Update carrying capacity based on STR
query_str/dex/con/int/wis/cha()  // Get stat values
set_experience(int xp)         // Set character XP total
```

#### Difficulty Level: **EASY**
- Well-isolated stat calculation in `stats.c`
- Easy to modify dice pools, bonuses, formulas
- Changing leveling curve requires editing `recalc_stats()` and guild objects only

---

### 3. SPELL & MAGIC SYSTEM

**Location:** `/lib/std/living/spells.c`, `/lib/std/spells/examples/`, spell instances

#### Spell Architecture:

**Base Spell Class** (`/lib/std/spells/examples/base.c`):
```lpc
spell_name              // Name of spell
sphere                  // Magic sphere (air, fire, etc.)
school                  // Magic school (evocation, abjuration, etc.)
spell_level             // 1-9 spell tier
target_type             // "self", "object", "room", "area", etc.
casting_time            // Rounds to cast (1-many)
gp_cost                 // Magic power cost
spell_range             // Maximum casting distance
line_of_sight_needed    // Line of sight required?
property_checks         // Properties preventing casting (stunned, silenced, etc.)
round[]                 // What happens each casting round (functions or messages)
```

**Spell Effect Management** (`/lib/std/living/spells.c`):
- Effects stored as array: `{ type, name, rounds, caster_obj, function, params }`
- Effects ticked down each combat round
- Automatic concentration loss if caster takes damage > 1/5 max HP
- Multiple instances of same spell type stacked or replaced

#### Spell Creation Process:

1. Create file inheriting `/lib/std/spells/examples/base.c`:
```lpc
inherit "/std/spells/examples/base.c";

void create() {
    ::create();
    set_spell_name("My Spell");
    set_spell_level(3);
    set_gp_cost(15);
    set_casting_time(2);
    set_target_type("object");
    // ... more setup
}

void setup() {
    // Called after create() to define rounds of casting
    set_rounds(({
        "You begin chanting mystic words...",
        "Your spell shimmers and releases!"
    }));
}
```

2. Implement spell effect function in calling object or separate module
3. Register spell with guild's spell directory

#### Key Functions:

```lpc
add_spell_effect(rounds, type, name, caster, function, params)
remove_spell_effect(name)
query_spell_effect(name)           // Get effect data
do_spell_effects(attacker)         // Tick all active effects
```

#### Customization Points:

- **Create new spells**: Inherit base.c, customize in spell directory
- **Add new spell spheres**: Modify SPECIALISTS file
- **Change casting mechanics**: Override `setup_weapon()` and casting loop
- **New effect types**: Extend `add_spell_effect()` and `do_spell_effects()`
- **Implement permaspells/auras**: Use `add_spell_effect()` at character init

#### Difficulty Level: **EASY to MEDIUM**
- Creating new spells is trivial (copy template, fill in values)
- Advanced spell mechanics (damage formulas, area effects) require function knowledge
- Integrating spells with skills requires modifying guild skill system

---

### 4. SKILL SYSTEM

**Location:** `/lib/std/skills.c`, `/lib/std/living/skills.c`

#### Skill Architecture:

**Skill Tree Structure:**
- Hierarchical skill tree with parent/child relationships
- Format: `skill.parent.child` (e.g., `melee.swords.longsword`)
- Stored in `/lib/std/skills.h` as STD_SKILLS array

**Skill Cost Model:**
- Flat cost to learn skill (skill points or XP)
- Cost scales with depth in tree (parent skills cheaper than children)
- Guild can override costs via `query_skill_cost(skill)`

**Skill Bonus Calculation:**
```lpc
query_skill_bonus(skill) returns:
  = base_skill_level 
    + stat_bonus (e.g., DEX for "dodge", STR for "melee")
    + guild_bonus (class-specific multipliers)
    + race_bonus (racial modifiers)
    + cache[skill]  // Fast lookups
```

#### Skill Usage:

Skills accessed via:
```lpc
obj->query_skill("melee.swords.longsword")     // Get raw skill level
obj->query_skill_bonus("melee.swords.longsword")  // Get bonus with stat mods
obj->add_skill_level(skill, levels, exp)       // Gain skill levels
```

#### Key Functions:

```lpc
query_skill_path(string skill)              // Get tree path array
register_skill(string skill)                // Add new skill to tree
remove_skill(string skill)                  // Remove skill from tree
add_stat_bonus(skill, bonus_stat)          // Link skill to stat
query_skill_bonus(skill)                   // Get modified skill value
```

#### Customization Points:

- **Add new skills**: Call `register_skill("parent.child")` from game startup
- **Create skill trees**: Modify STD_SKILLS array in `/lib/std/skills.h`
- **Change skill bonuses**: Modify `calc_bonus()` in `/lib/std/living/skills.c`
- **Link skills to abilities**: Override guild's `query_skill_bonus()` to apply multipliers
- **Implement skill checks**: Call `query_skill_bonus()` in combat/action code

#### Difficulty Level: **EASY**
- Skill tree is simple flat array structure
- Adding skills is just registering names
- Stat bonuses automatically calculated from skill path
- No complex dependencies or interactions

---

### 5. CHARACTER CLASSES (GUILDS)

**Location:** `/lib/std/guild.c`, `/lib/std/guilds/*.c`

#### Guild System Overview:

"Guilds" are the mudlib's class system. Each guild defines:
- **Main skill** (e.g., STR for fighters, INT for mages)
- **HP dice** (d6 for rogues, d10 for fighters)
- **Starting abilities** (special commands like "disarm", "focus", etc.)
- **Legal races/weapons/armor**
- **Skill bonuses** (multipliers to base skill levels)
- **Special mechanics** (dual wield penalties, extreme stat bonuses, etc.)

#### Guild Structure:

```lpc
// /lib/std/guilds/fighter.c example:
inherit "/std/guild";

void setup() {
    set_name("fighter");
    set_main_skill("str");
    add_guild_command("judge", 1);     // Player can use "judge" command
    add_guild_command("focus", 1);     // Focus attacks
    add_guild_command("smash", 1);     // Power attack
}

int query_advance_cost() { return 500; }  // Gold to advance level
int query_xp_cost() { return 2000; }      // XP to advance
int query_dice() { return 10; }           // d10 for HP
int query_thac0_step() { return 6; }      // THAC0 improves every 6 levels
int query_dual_wield_penalty(object me, w1, w2) { return 50 - level*2; }
```

#### Guild System Functions:

```lpc
set_main_skill(string stat)                // Set primary stat
add_guild_command(name, add_if_player)    // Add guild-specific command
query_main_skill()                         // Get primary stat
query_advance_cost()                       // Gold cost to level
query_xp_cost()                           // XP cost to level
query_dice()                              // Hit die size (d6, d8, d10, d12)
query_legal_race(race)                    // Can this race join?
query_legal_weapon(weapon_type)           // Can they use this weapon?
query_legal_armour(armor_type)            // Can they wear this?
query_skill_bonus(level, skill)           // Skill multiplier for guild
start_player(player_obj)                  // Called when player joins guild
on_death(player_obj, killer_obj)          // Called when player dies
query_title(player_obj)                   // Generate player title
```

#### Built-in Guilds:

1. **Fighter**: d10 HP, STR main, all weapons/armor, tank role
2. **Mage**: d6 HP, INT main, limited weapons, spell-focused
3. **Rogue**: d8 HP, DEX main, light weapons, versatile
4. **Cleric**: d8 HP, WIS main, medium weapons, healing/support
5. **Warrior**: Alternative fighter variant

**Subguild System:** `/lib/std/guilds/priests/` and `/lib/std/guilds/wizards/` directories exist for specializations.

#### Customization Points:

- **Create new class**: Create file in `/lib/std/guilds/newclass.c`, inherit `guild.c`
- **Modify existing class**: Edit guild file directly to change costs, dice, bonuses
- **Add class-specific commands**: Use `add_guild_command()` in setup
- **Implement class mechanics**: Override functions like `query_dual_wield_penalty()`
- **Create multiclass system**: Modify `/lib/std/guild.c` base to support multiple guild objects
- **Adjust level curve**: Modify `query_advance_cost()` and `query_xp_cost()`

#### Difficulty Level: **EASY**
- Guild creation is straightforward inheritance + function overrides
- No complex interdependencies
- Can copy existing guild file and modify for new class
- Adding subguilds just requires creating new guild files in subdirectories

---

### 6. RACIAL SYSTEM

**Location:** `/lib/std/race.c`, `/lib/std/races/*.c`

#### Race Architecture:

Each race defines:
- **Base height** (for visibility/combat modifiers)
- **Sight modifiers** (darkness sensitivity, brightness discomfort)
- **Stat adjustments** (racial bonuses to abilities)
- **Body parts** (limbs, health areas)
- **Attack types** (claws, bites, spells, weapons)
- **Armor coverage** (areas that need armor)
- **Dietary restrictions** (what can be eaten)

#### Race Structure:

```lpc
// /lib/std/races/elf.c example:
inherit "/std/races/base";

void setup() {
    set_height(167);                    // cm
    set_sight(({ 10, 20, 200, 250 })); // darkness/brightness thresholds
    
    // Stat modifications at character creation
    set_stat_modifiers(([
        "str" : -1,
        "dex" : 1,
        "con" : -1,
        "int" : 1,
    ]));
    
    // Define body parts
    add_bit(({...})); // Complex structure for limbs
    
    // Attack types and chances
    add_attack("bite", 20, ({ 1, 4 }));    // 20% chance, 1d4 damage
    
    // Armor class per area
    add_ac("head", "body", -2);             // Head AC modifier
}
```

#### Key Functions:

```lpc
query_height()                      // Base height in cm
set_sight(array)                   // Set light/dark visibility thresholds
set_stat_modifiers(mapping)        // Stat bonuses for race
query_stat_modifiers()             // Get stat bonuses
add_bit(array)                     // Add limb/body part
query_attacks()                    // Get all attack options
add_ac(name, type, bonus)          // Add armor class modifier
```

#### Available Races:

- Standard: Human, Elf, Dwarf, Gnome, Halfling, Half-Elf, Half-Orc, Drow
- Humanoid: Goblin, Orc, Lizard-Man
- Non-humanoid: Bird, Fish, Insect, Amphibian, Undead
- Special: Immortal, God, Unknown

#### Customization Points:

- **Create new race**: Create file in `/lib/std/races/newrace.c`, inherit `base.c`
- **Adjust stat modifiers**: Edit race file stat adjustment
- **Add racial abilities**: Implement via spells/skills and register to race
- **Modify racial restrictions**: Change `query_legal_weapon()`, `query_legal_armor()`
- **Create subraces**: Create subdir with racial variants
- **Implement racial prerequisites**: Add requirement checking to guild/skill systems

#### Difficulty Level: **MEDIUM**
- Race structure is moderately complex (body parts, armor coverage)
- Racial mechanics are relatively isolated but stat bonuses integrate with leveling
- Adding simple races is easy; complex anatomy requires understanding limb system

---

### 7. EQUIPMENT & INVENTORY SYSTEM

**Location:** `/lib/std/item.c`, `/lib/std/living/equip.c`, `/lib/std/basic/item_misc.c`

#### Equipment Architecture:

**Equipment Classes:**
- **Base**: `/lib/std/item.c` - All wearable/holdable items
- **Weapons**: Inherit `/std/weapon.c`
- **Armor**: Inherit `/std/armour.c`
- **Generic Items**: Inherit `/std/item.c`

**Equipment Slots:**
- Head, Body, Hands, Feet, Neck, Waist, Finger (multiple), Back
- Held (1 item per hand, supports 2-handed weapons)
- Worn (body parts)

**Item Properties:**
```lpc
set_wearable(1)         // Can be worn on body
set_holdable(1)         // Can be held in hands
set_armour_type(type)   // Type of armor (leather, plate, etc.)
set_weight(int)         // Encumbrance
set_size(int)           // Size category (affects fitting)
set_hands_needed(int)   // 1 or 2 hands required
```

#### Weapon System:

**Weapon Definition:**
```lpc
// in weapon file:
setup_weapon(
    "table_name",       // Weapon table for damage (e.g., "sword")
    "skill_name",       // Skill used (e.g., "melee.swords")
    normal_bonus,       // Non-magical bonus
    magic_bonus,        // Magical bonus
    "extra_code_func"   // Optional special effect function
);
```

**Weapon Mechanics:**
- Damage determined by weapon table + dice
- Bonuses applied separately (highest of normal/magic used)
- Can have special effects via `extra_code_func`
- Fumble ranges defined per weapon

#### Customization Points:

- **Create new weapon**: Inherit `/lib/std/weapon.c`, call `setup_weapon()`
- **New armor types**: Inherit `/lib/std/armour.c`, set armor coverage and AC
- **Enchantment system**: Modify `magic_bonus` dynamically, add property flags
- **Item effects**: Add spell effects to items on wield (e.g., fire aura)
- **Special weapon abilities**: Implement via `extra_code_func` callback
- **Container system**: Items can contain other items (no crafting by default)

#### Difficulty Level: **MEDIUM**
- Basic item creation is easy
- Weapon damage formula is somewhat complex (integrated with combat system)
- Armor AC calculation is straightforward
- Creating enchantment/special ability systems requires extending item properties

---

### 8. CRAFTING SYSTEM

**Status:** NOT IMPLEMENTED (system not found in codebase)

**Observations:**
- No dedicated crafting, alchemy, or forging system exists
- Weapons and armor are static objects created by builders
- No skill-based item creation or modification
- No resource gathering system

**Integration Path if Desired:**
1. Create `/lib/std/crafting.c` inheriting `/lib/std/object`
2. Define craft skills and recipes
3. Add crafting commands to guilds
4. Integrate with skill system for success/failure
5. Could tie to new items or item modification system

#### Difficulty Level if Implementing: **HARD**
- Would require creating entire subsystem
- Integration with skills, items, and guilds needed
- Quest/gathering systems would also need development
- Substantial development effort required

---

## Customization Guide by System

### Quick Reference: Difficulty Levels by Modification Type

| System | Difficulty | Reason | Typical Time |
|--------|-----------|--------|--------------|
| Add new spell | Easy | Template provided, just fill values | 30 min |
| Add new skill | Easy | Simple registration, no dependencies | 15 min |
| Add new guild/class | Easy | Inherit guild.c, override functions | 1-2 hours |
| Add new race | Medium | Body parts complex, stat system easy | 2-4 hours |
| New weapon type | Medium | Damage formulas need integration | 1-2 hours |
| Change damage formula | Medium | Scattered across combat/weapon files | 2-4 hours |
| Implement crafting | Hard | New system with multiple dependencies | 8-16 hours |
| Overhaul combat system | Hard | Deeply integrated with multiple systems | 16+ hours |
| New magic school | Medium | Requires spell registration + sphere | 2-4 hours |
| Implement permaspells | Medium | Integrate with spell effect system | 2-3 hours |

### Specific Customization Examples

#### Example 1: Add a New Guild (Paladin Class)

**Steps:**
1. Create `/lib/std/guilds/paladin.c`:
```lpc
inherit "/std/guild";

void setup() {
    set_name("paladin");
    set_short("paladin");
    set_long("Holy warriors blessed with divine power...");
    set_main_skill("str");
    add_guild_command("smite", 1);
    add_guild_command("lay_hands", 1);
    set_needed_align("good");  // Only good alignment
}

void create() {
    ::create();
    set_main_skill("str");
}

int query_dice() { return 10; }
int query_advance_cost() { return 600; }
int query_xp_cost() { return 2500; }
int query_legal_race(string race) { 
    return (race != "drow" && race != "orc"); 
}
```

2. Create paladin-specific spells in `/lib/d/guilds/paladins/`
3. Add "paladin" to list of available guilds in login system
4. Optionally shadow player with `/lib/std/shadows/paladin_shadow.c` for special mechanics

**Time:** 1-2 hours

---

#### Example 2: Add a New Spell Type

**Steps:**
1. Create `/lib/std/spells/examples/my_spell.c`:
```lpc
inherit "/lib/std/spells/examples/base.c";

void create() {
    ::create();
    set_spell_name("Fireball");
    set_sphere("evocation");
    set_school("evocation");
    set_spell_level(4);
    set_gp_cost(25);
    set_casting_time(2);
    set_target_type("area");
    set_range(50);
    set_rounds(({
        "You raise your hand and gather mystical energy.",
        "A ball of flame erupts from your fingers!"
    }));
}

void setup() {
    // Setup inherited from base
}

// This will be called by the spell effect system
int cast_effect(object caster, object *targets, mixed param, int rounds) {
    int i, dam;
    for (i = 0; i < sizeof(targets); i++) {
        if (targets[i]) {
            dam = random(10) + 15;
            targets[i]->adjust_hp(-dam);
        }
    }
    return 0;  // XP return
}
```

2. Register spell with guild in `/lib/std/guilds/mage.c` (if not auto-loaded)

**Time:** 30 minutes

---

#### Example 3: Modify Combat Damage Formula

**Steps:**
1. Locate `/lib/std/living/combat.c` and `/lib/std/weapon_logic.c`
2. Find `apply_damage()` function in weapon_logic.c
3. Modify damage calculation:
```lpc
void apply_damage(int hps) {
    // Original might be:
    // damage = base_weapon_dice + str_bonus + magic_bonus
    
    // New formula with armor penetration:
    int armor_reduction = defender->query_total_ac() / 2;
    int final_damage = hps - armor_reduction;
    
    if (final_damage > 0)
        defender->adjust_hp(-final_damage, attacker);
}
```

4. Test with combat
5. Adjust formulas until balanced

**Time:** 2-4 hours (including testing/balancing)

---

#### Example 4: Add a New Skill Tree

**Steps:**
1. Modify `/lib/std/skills.h` STD_SKILLS array to add new skill:
```lpc
// OLD: melee.swords.longsword
// NEW: melee.swords.longsword
//      melee.magic_weapons.runesword
//
// In skills.c skills definition tree:
STD_SKILLS = ({
    "melee", 0, 0, ({
        "swords", 0, 0, ({
            "longsword", 0, 0, ({}),
            "shortsword", 0, 0, ({}),
        }),
        "magic_weapons", 0, 0, ({
            "runesword", 0, 0, ({}),
        }),
    }),
    // ... rest of skills
});
```

2. Register with skills system:
```lpc
// In game initialization:
SKILLS->register_skill("melee.magic_weapons.runesword");
SKILLS->add_stat_bonus("melee.magic_weapons", "I");  // Intelligence bonus
```

3. Create items that use skill:
```lpc
// In weapon file:
setup_weapon("runesword", "melee.magic_weapons.runesword", 50, 50, 0);
```

**Time:** 30-45 minutes

---

### Modification Strategy by Need

#### "I want to make combat faster/slower"
- **Modify:** `/lib/std/living/combat.c` attack loop interval
- **Or modify:** THAC0 calculation to affect hit chance

#### "I want to add new damage types (fire, cold, etc.)"
- **Create:** Resistance properties on characters
- **Modify:** Damage application to check resistances
- **Integrate:** Via spell effects or item properties

#### "I want to implement a reputation/faction system"
- **Create:** `/lib/std/living/reputation.c`
- **Inherit:** From living.c
- **Add:** Tracking of faction standing
- **Modify:** Guild/skill access based on reputation

#### "I want permabuffs/auras"
- **Use:** `add_spell_effect()` at character initialization
- **Set:** Very high round count (or infinite if modified)
- **Modify:** `do_spell_effects()` to skip removing long-duration effects

#### "I want to implement dual-wielding properly"
- **Modify:** `/lib/std/living/equip.c` to allow two weapons
- **Modify:** `/lib/std/living/combat.c` attack() to hit with both weapons
- **Create:** Guild-specific `query_dual_wield_penalty()` to control accuracy loss

---

## Integration Points & Extensibility

### Key Extension Hooks

**1. Character Creation**
- Location: Where players join guild and race
- Hook: `guild->start_player(player)` - customize character at jointime
- Hook: `race->setup()` - apply racial traits

**2. Level Gain**
- Location: `/lib/std/living/stats.c` `recalc_stats()`
- Hook: Override to add custom level-up bonuses
- Hook: Can distribute skill points automatically

**3. Combat Round**
- Location: `/lib/std/living/combat.c` `attack()`
- Hook: Add special effects before/after attacks
- Hook: Modify targeting logic

**4. Spell Casting**
- Location: `/lib/std/living/spells.c` `add_spell_effect()`
- Hook: Add prerequisites checks
- Hook: Modify effect duration/power

**5. Skill Checks**
- Location: Anywhere `query_skill_bonus()` is called
- Hook: Override to apply modifiers
- Hook: Add skill check randomization

**6. Item Equipping**
- Location: `/lib/std/living/equip.c` `do_wear()`, `do_hold()`
- Hook: Add equipment effects
- Hook: Check equipment restrictions

**7. Death/Resurrection**
- Location: `/lib/std/living/death.c`
- Hook: Custom death mechanics
- Hook: Experience loss, corpse handling

---

### Recommended Customization Areas (Easiest to Start)

1. **Create 2-3 new guilds** - Good practice, no dependencies
2. **Add 5-10 new spells** - Template-based, learn spell system
3. **Create 2-3 new races** - Understand character stats
4. **Add guild-specific commands** - Learn skill system integration
5. **Modify a few skill bonuses** - Practice number tuning
6. **Create special weapon** - Integrate with combat system
7. **Add faction/reputation** - Create new character property system
8. **Implement simple quest system** - Integrate with NPCs/rewards
9. **Create permabuff system** - Extend spell effect system
10. **Overhaul damage formula** - Advanced system modification

---

## Difficulty Assessment Summary

### Overall Customization Difficulty: **MEDIUM**

**Strengths (Easy to Customize):**
- ✅ Adding new content (spells, skills, items, classes) is trivial
- ✅ Number tweaking (damage, costs, bonuses) is straightforward
- ✅ Modular architecture prevents changes from breaking other systems
- ✅ Well-documented class templates and examples
- ✅ Inheritance-based design makes extending easy
- ✅ Can create new systems without modifying core files

**Weaknesses (Hard to Customize):**
- ❌ Combat system is interconnected (stats, weapons, armor, spells)
- ❌ No built-in crafting/gathering systems (would need development)
- ❌ Spell effect system is simple but limited for complex mechanics
- ❌ Dual-wield system not well-integrated (would need workarounds)
- ❌ No explicit skill point system (skills auto-advance with levels)
- ❌ Limited property/enchantment system for items

### Best Use Cases for This Mudlib:

1. **Fantasy combat MUD** - Excellent combat system
2. **Class/race exploration** - Easy to create many variants
3. **Spell-heavy MUD** - Good spell framework
4. **Skill-based progression** - Flexible skill tree system
5. **Guild-based MUD** - Native guild support

### Worst Use Cases:

1. **Crafting/economy focus** - No crafting system
2. **Complex quest chains** - No built-in quest system
3. **Permadeath PvP** - Death mechanics are simple
4. **Tactical grid combat** - Too abstract for grid-based system
5. **Complex skill point allocation** - Skills auto-advance, can't prevent

---

## File Reference Guide

### Essential Files to Know

| File | Purpose | Modification Frequency |
|------|---------|------------------------|
| `/lib/std/living.c` | Base character object | Rarely (core) |
| `/lib/std/living/combat.c` | Combat system | Sometimes |
| `/lib/std/living/spells.c` | Spell effects | Sometimes |
| `/lib/std/living/skills.c` | Skill system | Often |
| `/lib/std/living/stats.c` | Attributes/HP/GP | Sometimes |
| `/lib/std/guild.c` | Class base | Often (create subclasses) |
| `/lib/std/guilds/*.c` | Guild implementations | Often |
| `/lib/std/races/*.c` | Race implementations | Often |
| `/lib/std/spells/examples/base.c` | Spell template | Often (inherit) |
| `/lib/std/item.c` | Item base class | Rarely |
| `/lib/std/weapon_logic.c` | Damage calculation | Sometimes |
| `/lib/std/skills.c` | Global skill registry | Sometimes |

### Build & Test Files

| File | Purpose |
|------|---------|
| `/lib/std/living/livingtest.c` | Living object test |
| `/lib/std/living/combattest.c` | Combat test |
| `/lib/std/living/spellstest.c` | Spell test |
| `/lib/std/living/equiptest.c` | Equipment test |

---

## Conclusion

**Final Realms is an excellent foundation for building a fantasy MUD**, particularly if you:
- Want to create varied guilds, races, spells, and skills
- Need a solid combat system to build upon
- Plan to customize through inheritance and templating
- Aren't building around crafting/economy as a core mechanic

**Estimated time to understand core systems:** 4-8 hours of code review  
**Estimated time to make simple customizations:** 1-4 hours per feature  
**Estimated time to overhaul a major system:** 8-16+ hours  

The architecture strongly encourages adding new content rather than modifying existing systems, which is a healthy design pattern for long-term maintenance.

---

*Document generated: November 2024*  
*Mudlib: Final Realms v1 (FluffOS 2.9)*
