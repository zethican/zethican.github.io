# **ZD12 RPG Implementation Roadmap**

## 1. Understanding the Goal

The objective is to create a comprehensive roadmap for implementing the ZD12 RPG system into the existing LIL MUDlib codebase. The implementation should draw its lore and rules from the `zd12_2.8.2.md` document, while ensuring that no critical conflicts with the current mudlib are introduced. This document outlines the strategic plan for this endeavor.

**Disclaimer:** The `zd12_2.8.2.md` document was not provided. This plan is based on an assumed, generic RPG structure and will need to be adapted once the specifics of the ZD12 system are known.

## 2. Investigation & Analysis

A thorough understanding of both the ZD12 system and the LIL MUDlib is critical before any implementation begins. The following investigative steps are recommended:

* **ZD12 System Analysis:**
  
  * A complete review of `zd12_2.8.2.md` to identify:
    * **Core Attributes:** (e.g., Strength, Dexterity, Intelligence)
    * **Derived Statistics:** (e.g., Health, Mana, Stamina)
    * **Skill System:** A list of all skills and their mechanics.
    * **Combat System:** Rules for initiative, attack rolls, damage calculation, and defense.
    * **Magic/Special Abilities:** A list of all spells and special abilities.
    * **Inventory and Equipment:** Rules for item slots, encumbrance, and item properties.
    * **Character Progression:** Experience points, leveling, and advancement mechanics.

* **LIL MUDlib Analysis:**
  
  * **Player Object (`clone/user.c`):** Analyze this file to understand how player data is stored and managed. This will be the primary location for adding new ZD12-specific attributes.
  * **NPC Object (`obj/monster` - assumed location):** Based on `GEMINI.md`, this is the base for NPCs. This will need to be extended to support ZD12 combat and skill mechanics.
  * **Combat Mechanics:** Search the `command/` directory for existing combat commands. The `GEMINI.md` file mentions `load_a_chat()` for combat lines, which implies a combat system exists. The extent of this system needs to be determined.
  * **Standard Objects:** The `GEMINI.md` file details the use of `std/room/outside.c` and `std/room/basic_room.c` for rooms, and virtual objects for items (`.clo`, `.arm`). These will be the foundation for creating the ZD12 world.
  * **Inheritance Structure:** The `inherit/` directory, especially `base.c`, will reveal the core functionality that all objects in the MUD share.
  * **Header Files (`include/`):** Files like `config.h`, `globals.h`, and `lpctypes.h` will provide insight into the MUD's configuration and data structures.

## 3. Proposed Strategic Approach

The implementation will be broken down into the following phases:

### Phase 1: Foundational Systems (The "Character Sheet")

This phase focuses on integrating the core ZD12 character data into the MUD.

1. **Player Object Extension:**
   * Modify `clone/user.c` to add data members for all ZD12 core attributes, derived statistics, and other character-specific data (e.g., experience points, level).
   * Ensure this data is saved and loaded correctly when the player logs in and out.
2. **Character Sheet Command:**
   * Create a new command (e.g., `score`, `sheet`) that displays the player's ZD12 attributes and statistics in a user-friendly format.
3. **NPC Object Extension:**
   * Modify the base NPC object (`obj/monster`) to include the same ZD12 attributes as players. This will allow for consistent mechanics for both players and NPCs.

### Phase 2: Core Mechanics (The "Dice Rolls")

This phase implements the fundamental ZD12 rules.

1. **Skill System:**
   * Create a new `skill` object or a system within the player object to manage skills.
   * Implement a `skill_check()` efun or function that can be called from any object to perform a skill roll based on ZD12 rules.
2. **Basic Combat:**
   * Modify the existing combat system or create a new one to use ZD12 combat rules. This will involve:
     * Modifying the `kill` command to initiate combat.
     * Creating a combat "heartbeat" that processes rounds of combat.
     * Implementing ZD12's formulas for attack rolls, damage, and defense.
3. **Item Integration:**
   * Extend the virtual object format to include ZD12-specific item properties (e.g., weapon damage, armor class).
   * Modify the `wield` and `wear` commands to apply these properties to the player's character sheet.

### Phase 3: Content Creation (The "World Building")

With the core systems in place, this phase is about populating the world.

1. **Create a ZD12 Zone:**
   * Create a new directory in the MUD's world files for a dedicated ZD12 area.
   * Build a small number of rooms, NPCs, and items using the new ZD12 systems. This will serve as a testbed and a template for future content.
2. **Develop Content Creation Guidelines:**
   * Create a document for builders that explains how to create ZD12-compliant rooms, NPCs, and items. This will be an addendum to the existing `GEMINI.md`.

### Phase 4: Advanced Systems (The "Magic and More")

This phase implements the more complex ZD12 systems.

1. **Magic/Special Abilities:**
   * Create a `spell` object and a `cast` command.
   * Implement the effects of each spell and special ability as defined in the ZD12 rules.
2. **Quests and Progression:**
   * Create a questing system that can be used to guide players through the ZD12 content.
   * Implement the experience point and leveling system.

## 4. Verification Strategy

* **Unit Testing:**
  * The `single/tests/` directory suggests a testing framework is in place. New tests should be written for all new ZD12 systems, including:
    * Tests for the `skill_check()` function.
    * Tests for combat calculations.
    * Tests for item property application.
* **Integration Testing:**
  * The ZD12 test zone will be used for manual, interactive testing of the new systems.
* **Player Feedback:**
  * Once the core systems are stable, a beta testing phase will be initiated to gather feedback from players on balance, usability, and fun.

## 5. Anticipated Challenges & Considerations

* **System Conflicts:** The biggest risk is introducing changes that conflict with the existing MUDlib. A thorough understanding of the MUDlib's architecture is crucial to avoid this. All changes should be made in a modular and isolated way where possible.
* **Balancing:** RPG system balancing is a complex and ongoing process. The initial implementation will likely require significant tuning based on player feedback.
* **Scope Creep:** The ZD12 rulebook may be extensive. It is important to focus on implementing the core systems first and then adding more complex features over time.
* **Documentation:** The `GEMINI.md` file is an excellent example of good documentation. This project should maintain the same high standard of documentation for all new systems and content.