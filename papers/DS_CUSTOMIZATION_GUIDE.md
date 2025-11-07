# Dead Souls 2 Customization Overview

## Summary

This is a **highly modular, well-documented LPC MUD library** based on the classic Nightmare IV architecture. **Customization is quite feasible** for adding new game systems or modifying existing ones. The library uses object-oriented inheritance and configuration files to keep code DRY and maintainable.

---

## 1. GAME SYSTEMS ARCHITECTURE

### Skills System (Moderate Difficulty: ⭐⭐⭐)

**Location:** `/lib/daemon/skills.c`, `/lib/daemon/classes.c`

**How it works:**

- Skills are defined **per-class** and can be **per-race**
- Each skill has a base "SkillClass" value (difficulty/complexity tier)
- Classes reference skills via configuration files in `/lib/cfg/`
- Skills are stored in mappings: `Skills[skillname][classname] = skillclass`

**Customizability:**

- ✅ **Easy to add new skills:** Add to class/race config files and call `SKILLS_D->SetSkill()`
- ✅ **Skill depth is configurable** - set via numeric skill class values
- ✅ **Multi-classing partially supported** - code exists for multi-class logic
- **Note:** Skill trees/prerequisites would require extending `skills.c`

**Example:** Skills are granular - you can have "blade attack", "blade defense", "fire magic", "cold magic", etc.

---

### Stats System (Easy Difficulty: ⭐)

**Location:** `/lib/daemon/stats.c`, `/lib/include/body_types.h`

**How it works:**

- Core stats are **race-based** (defined per-race in config)
- Each stat has a "Class" value (numeric tier)
- Living objects inherit from `LIB_BODY` which manages stats

**Customizability:**

- ✅ **Very easy to add new stats:** Add to race definition + call `STATS_D->SetStat()`
- ✅ **Stats are completely configurable** - just numeric values
- ✅ **Can add arbitrary trackers** - just add more stat entries
- **Current trackers visible in `/lib/lib/body.c` line 39-42:**
  - `HealthPoints, MagicPoints, ExperiencePoints, ExperienceDebt`
  - `Alcohol, Caffeine, Food, Drink, Poison, Sleeping`
  - `StaminaPoints`

**How to add Thirst/Hunger:** Just add `Thirst` and `Hunger` as new variables in `body.c`, then add getter/setter functions. Approximately **10-15 lines of code per new tracker**.

---

### Weapons System (Easy to Moderate Difficulty: ⭐⭐)

**Location:** `/lib/obj/weapon.c`, `/lib/obj/sword.c` (example)

**How it works:**

- All items inherit from `LIB_ITEM` (generic base)
- Weapons are configured with:
  - `SetClass()` - damage class (1-100 scale)
  - `SetWeaponType()` - "blade", "knife", "blunt", "projectile"
  - `SetDamageType()` - type constants from `/include/damage_types.h`
  - Optional `SetWield()` function for special behaviors

**Customizability:**

- ✅ **Not deeply hardcoded** - easy to create new weapon types
- ✅ **Weapon types are extensible** - just add new type strings
- ✅ **Damage modification is flexible:**
  - Override `eventStrike()` for custom damage calculations
  - Override `eventReceiveDamage()` for special effects
  - Add stat bonuses via `AddStatBonus()` / `AddSkillBonus()`
- ✅ **Combat event system is well-documented** (see `/doc/build/Weapons`)

**Example:** Creating a new weapon type takes ~20-30 lines. Special effects (poison, enchantments, etc.) can be added via event overrides.

---

### Magic/Spells System (Moderate Difficulty: ⭐⭐⭐)

**Location:** `/lib/daemon/spells.c`, `/lib/include/magic.h`

**How it works:**

- Spells are **dynamically loaded** from `/lib/spells/` and `/lib/prayers/`
- Daemon loads all `.c` files from these directories
- Each spell calls `GetSpell()` to return its name
- Spells/prayers are stored in separate mappings but accessed the same way

**Magic categories (from `/include/magic.h`):**

```c
#define SPELL_HEALING       1
#define SPELL_DEFENSE       2
#define SPELL_COMBAT        3
#define SPELL_OTHER         4
```

**Customizability:**

- ✅ **Not hardcoded** - just create new `.c` files in the spell directories
- ✅ **Categories are easily extensible** - add new `#define` constants
- ✅ **Spells are loaded dynamically** - can reload without restart
- ⚠️ **Spell mechanics require custom coding** - you define what each spell does
- **Limitation:** Spell system is basic - just name/storage. Actual casting logic is on the player/class side.

**Tip:** Each spell file should inherit from a base spell class (not visible but referenced in design).

---

### Combat System (Moderate-Hard Difficulty: ⭐⭐⭐)

**Location:** `/lib/lib/combat.c`, `/lib/lib/combatmsg.c`

**How it works:**

- Event-driven combat system with multiple phases:
  1. Check if attacker can hit (skill-based)
  2. Check if target dodges (skill-based)
  3. `eventStrike()` called on weapon
  4. `eventReceiveDamage()` called on target (triggers armor calculations)
  5. Skill/stat gains processed
- Combat constants defined (e.g., `MAX_ATTACKS_PER_HB = 40`)
- Support for multiple attack types: weapon, melee, magic

**Customizability:**

- ✅ **Modular attack types** - weapon/melee/magic are separate code paths
- ✅ **Skill-based hit calculation** - skills affect accuracy/dodge
- ✅ **Armor integration** - armor receives damage in event chain
- ⚠️ **Some hardcoded constants** exist (MAX_POWER=9001, MAX_SKILL=1000)
- **Relatively complex** - understand event flow before customizing

---

## 2. ADDING NEW TRACKERS (Thirst, Hunger, etc.)

**Difficulty: Easy (⭐)**

Here's how to add a new tracker like "Thirst":

### Step 1: Add variable to `/lib/lib/body.c`

```c
private int Thirst;  // Add after line 42

static void create(){
    // ... existing code ...
    Thirst = 100;  // Initialize in create()
}
```

### Step 2: Add getter/setter

```c
int GetThirst() { return Thirst; }
void SetThirst(int val) { Thirst = val; }
```

### Step 3: Add decay/regeneration logic

- Add to `eventHeartbeat()` in `body.c` or create a new event

### Step 4: Integrate into player experience

- Check thirst in combat (`combat.c`)
- Show in `look` command (typically in `living.c`)

**Time estimate:** 30 minutes per new tracker

---

## 3. SKILL CATEGORIES DEPTH

**Current structure:**

- Classes have a list of skills (mapping)
- Each skill has a numeric "SkillClass" (difficulty tier)
- Skills are registered globally in `SKILLS_D` daemon

**Examples of skill granularity:**

- Generic: "magic", "combat", "defense"
- Specific: "blade attack", "fire magic", "dodge", "parry"
- The library doesn't restrict naming - you can be as specific as needed

**To add skill trees/prerequisites:**

- Extend `skills.c` to store skill dependencies
- Create `GetSkillPrerequisites()` function
- Check prerequisites before skill gain
- **Estimated effort:** 50-100 lines of code

---

## 4. CLASS & RACE SYSTEMS

**Location:** `/lib/daemon/classes.c`, `/lib/daemon/races.c`

**How it works:**

- Classes loaded from config files (look for `/lib/cfg/classes/`)
- Races loaded from config files (look for `/lib/cfg/races/`)
- Each defines:
  - Base stats (for races)
  - Available skills and their starting values
  - Special abilities/modifiers (for races: flying, swimming, limbless combat, etc.)

**Customizability:**

- ✅ **Very easy to add new classes/races** - just create config files
- ✅ **Racial traits are configurable** - flags like `CanFly()`, `CanSwim()`, `GetLimblessCombatRace()`
- ⚠️ **Multi-class support exists but incomplete** - the structure is there but not fully implemented

---

## 5. KEY DOCUMENTATION

Navigate to these files for deeper understanding:

| Topic                   | Location                       | Difficulty |
| ----------------------- | ------------------------------ | ---------- |
| Building weapons        | `/doc/build/Weapons`           | Easy       |
| Building NPCs/Sentients | `/doc/build/Sentients`         | Moderate   |
| General building intro  | `/doc/build/Introduction`      | Easy       |
| Building armors         | `/doc/build/Armours`           | Easy       |
| Combat flow details     | `/lib/lib/combat.c` lines 1-70 | Moderate   |

---

## 6. KEY CONFIGURATION LOCATIONS

| System        | Config Location                        | Format                     |
| ------------- | -------------------------------------- | -------------------------- |
| Time/Calendar | `/lib/cfg/` (time.cfg, days.cfg, etc.) | .cfg files                 |
| Classes       | Loaded dynamically, look in code       | Class definitions          |
| Races         | Loaded dynamically, look in code       | Race definitions           |
| Spells        | `/lib/spells/` and `/lib/prayers/`     | .c files (one per spell)   |
| Damage types  | `/include/damage_types.h`              | Header file with constants |
| Vendor types  | `/include/vendor_types.h`              | Header file with constants |

---

## 7. OVERALL CUSTOMIZATION DIFFICULTY RANKING

| Feature                             | Difficulty | Estimated Time |
| ----------------------------------- | ---------- | -------------- |
| Add new stat/tracker                | ⭐          | 30 min         |
| Add new weapon/item                 | ⭐          | 15 min         |
| Add new skill                       | ⭐⭐         | 30 min         |
| Add new class/race                  | ⭐⭐         | 1 hour         |
| Extend combat (new attack type)     | ⭐⭐⭐        | 2-3 hours      |
| Add spell magic system              | ⭐⭐⭐        | 2-4 hours      |
| Implement skill prerequisites/trees | ⭐⭐⭐        | 2-3 hours      |
| Add new damage type                 | ⭐          | 15 min         |
| Redesign armor system               | ⭐⭐⭐⭐       | 4-8 hours      |

---

## 8. DESIGN PHILOSOPHY

This library follows **"Object-Oriented Lego Blocks"**:

- **Inheritance:** Base classes (`LIB_ITEM`, `LIB_LIVING`, etc.) provide 80% of functionality
- **Configuration over Code:** Settings via `Set*()` calls rather than hardcoding
- **Event-Driven:** Objects react to events (`eventXXX()` functions) rather than polling
- **Modular Inheritance:** Use multiple inheritance to compose behaviors (see `/lib/living.c` - inherits 10+ base classes)

**This makes it:**

- ✅ Easy to extend with new features
- ✅ Hard to break existing systems
- ✅ Intuitive for creators familiar with OOP concepts

---

## 9. QUICK START: ADD A NEW TRACKER

Want to add Thirst/Hunger right now? Here's the minimal change:

**File:** `/lib/lib/body.c`

**Add these lines in `create()` (around line 69):**

```c
private int Hunger, Thirst;

static void create(){
    // ... existing code ...
    Hunger = 100;
    Thirst = 100;
}

int GetHunger() { return Hunger; }
void SetHunger(int val) { Hunger = clamp(val, 0, 100); }
int GetThirst() { return Thirst; }
void SetThirst(int val) { Thirst = clamp(val, 0, 100); }
```

Done! The stats are now part of every living object. Integrate into gameplay by:

- Decreasing in `eventHeartbeat()`
- Affecting combat performance in `combat.c`
- Showing in player `look` command

---

## Summary

**Easy to customize:** ✅ Stats, skills, weapons, items, classes, races
**Moderately complex:** ⭐⭐ Combat tweaks, spell systems, NPC AI
**Hard to customize:** ⭐⭐⭐ Core inheritance structure, engine-level changes

The library is **well-designed for extension** - most customizations require adding code, not modifying existing code. This is a **strong foundation for a customizable game**.