# Pick-Your-Own-Adventure Story Authoring Guide

Welcome! This guide explains how to write custom, data-driven stories for the Pick-Your-Own-Adventure game engine.

Each story lives in its own subdirectory inside the `stories/` folder and is defined by a single `story.yaml` file (accompanied by assets like images and music files).

---

## Directory Structure

A typical story directory should look like this:

```
stories/
└── your_story_id/
    ├── story.yaml             # The story file
    ├── cover.png              # Cover image (optional)
    ├── music/                 # Optional audio directory
    │   └── ambient.mp3
    └── sounds/                # Optional SFX directory
        └── click.mp3
```

---

## The `story.yaml` Format

The `story.yaml` file consists of three main top-level keys:
1. `meta`: Details about the story (title, author, cover, starting point).
2. `variables`: State variables representing player stats, inventory, or story choices.
3. `nodes`: The discrete scenes/chapters of the story.

Here is a full breakdown of each section.

---

## 1. Metadata (`meta`)

The `meta` block defines global details about the story.

```yaml
meta:
  id: your_story_id              # Unique string ID
  title: "The Golden Key"        # Title shown in the browser and game
  author: "Jane Doe"             # Author name
  version: "1.0"                 # Story version
  description: "A gothic tale..."# Short summary shown in the browser
  start_node: arrival            # ID of the starting node
  cover_image: cover.png         # Cover art filename (relative to story folder)
```

---

## 2. Variables (`variables`)

Variables track the game state. They can be simple (for internal variables) or rich (to display them on the **Character Sheet**).

### Simple Format
```yaml
variables:
  coins: 10
  has_key: false
```

### Rich Format
Use this format if you want a variable to be displayed on the Character Sheet.
```yaml
variables:
  reputation:
    value: 0                     # Initial value
    label: "Reputation"          # Human-readable name
    description: "Your standing" # Description on tooltip
    icon: "⭐"                    # Icon shown on Character Sheet
    category: "Stats"            # Category grouping on Character Sheet
    visible: true                # Set to false to hide from Character Sheet
    display_type: bar            # 'bar' | 'number' | 'boolean' | 'auto'
    min_value: -5                # Required for 'bar'
    max_value: 10                # Required for 'bar'
```

### Display Types:
- **`bar`**: Renders as a filled progress bar between `min_value` and `max_value`.
- **`number`**: Renders as a plain integer (e.g. `💰 Shillings: 15`).
- **`boolean`**: Renders as a colored badge: `✓` (green) if true, `✗` (dimmed) if false.
- **`auto`**: Auto-detects based on value type.

---

## 3. Story Nodes (`nodes`)

Each node is a scene/chapter in the adventure.

```yaml
nodes:
  arrival:
    title: "Ravenstone Manor"           # Chapter title shown in the Status Bar
    text: |
      You arrive at the gate. The iron bars are cold and wet.
      A single light burns on the third floor...
    music: music/arrival_ambient.mp3    # Loop music (path relative to story folder)
    sfx: sounds/thunder.mp3             # Sound effect played once on entry
    ending: false                       # Set to true if this is a terminal ending node
    choices:
      - text: "Ring the bell."
        next: announce_arrival
        sfx: sounds/bell.mp3            # Sound effect played on click
```

---

## 4. Choices, Conditions, and Effects

Each node has a list of choices. A choice can have conditions (restricting when it is shown) and effects (updating variables when selected).

### Conditions
All conditions in the list must evaluate to `True` for the choice to be visible to the player.

- **`require`**: Evaluates to `True` if the check passes.
- **`unless`**: Evaluates to `True` if the check fails (reverses the result).

#### Available Operators:
- `eq` (equal to)
- `ne` (not equal to)
- `gt` (greater than)
- `lt` (less than)
- `gte` (greater than or equal to)
- `lte` (less than or equal to)

#### Examples:
```yaml
# Simple boolean check (shorthand for eq: true)
conditions:
  - require: { has_lantern: true }

# Unless boolean check (shorthand for eq: false)
conditions:
  - unless: { has_lantern: true }

# Numeric comparisons
conditions:
  - require: { coins: { gte: 5 } }
  - require: { reputation: { lt: 3 } }
```

---

### Effects
Applied to variables in order when the choice is clicked, before navigating to the next node.

- **`set`**: Assigns a specific value to a variable.
- **`increment`**: Adds a value to a numeric variable.
- **`decrement`**: Subtracts a value from a numeric variable.
- **`toggle`**: Toggles a boolean variable between `true` and `false`.

#### Examples:
```yaml
effects:
  - set: { bribed_butler: true }
  - decrement: { coins: 5 }
  - increment: { reputation: 1 }
  - toggle: lantern_on
```

---

## Best Practices and Engine Features

1. **Audio Path Resolution**: All music and SFX paths are relative to the story directory. If an audio file is missing, the engine skips it gracefully without crashing.
2. **Auto-Save**: The game auto-saves the player's progress locally.
3. **Graceful Failures**: If a choice attempts to update a variable not defined in the `variables:` block, the engine will warn in logs but will not crash.
