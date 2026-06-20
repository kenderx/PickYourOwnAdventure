"""
theme.py
Color palettes and font definitions for all three themes.
All UI widgets pull their colours from app.colors (a dict from this module).
"""
from __future__ import annotations

# ---------------------------------------------------------------------------
# Color palettes
# ---------------------------------------------------------------------------

THEMES: dict[str, dict[str, str]] = {
    # ---- Dark (default) — deep violet on near-black ----
    "dark": {
        "bg_primary":    "#0d0d1a",
        "bg_secondary":  "#13132a",
        "bg_panel":      "#1a1a2e",
        "bg_card":       "#16213e",
        "bg_input":      "#0d0d20",
        "accent":        "#7c3aed",
        "accent_hover":  "#9d5ff5",
        "accent_dark":   "#5b21b6",
        "accent_glow":   "#7c3aed44",
        "text_primary":  "#e8e8f5",
        "text_secondary":"#9090b8",
        "text_muted":    "#55557a",
        "text_accent":   "#c4b5fd",
        "choice_bg":     "#16213e",
        "choice_hover":  "#221a4e",
        "choice_border": "#7c3aed",
        "btn_primary":   "#7c3aed",
        "btn_primary_h": "#9d5ff5",
        "btn_secondary": "#1f1f3a",
        "btn_secondary_h":"#2a2a50",
        "btn_danger":    "#7f1d1d",
        "btn_danger_h":  "#991b1b",
        "success":       "#10b981",
        "warning":       "#f59e0b",
        "danger":        "#ef4444",
        "border":        "#2a2a4a",
        "border_accent": "#7c3aed",
        "scrollbar":     "#7c3aed",
        "overlay":       "#0d0d1acc",
        "bar_track":     "#2a2a4a",
        "bar_fill":      "#7c3aed",
        "bar_fill_low":  "#ef4444",
        "separator":     "#2a2a4a",
    },

    # ---- Light — clean white with violet accents ----
    "light": {
        "bg_primary":    "#f0eff8",
        "bg_secondary":  "#e8e7f5",
        "bg_panel":      "#ffffff",
        "bg_card":       "#f5f3ff",
        "bg_input":      "#faf9ff",
        "accent":        "#6d28d9",
        "accent_hover":  "#7c3aed",
        "accent_dark":   "#4c1d95",
        "accent_glow":   "#7c3aed22",
        "text_primary":  "#1a1a2e",
        "text_secondary":"#4a4a6a",
        "text_muted":    "#8a8aaa",
        "text_accent":   "#5b21b6",
        "choice_bg":     "#ede9fe",
        "choice_hover":  "#ddd6fe",
        "choice_border": "#7c3aed",
        "btn_primary":   "#6d28d9",
        "btn_primary_h": "#7c3aed",
        "btn_secondary": "#e5e3f5",
        "btn_secondary_h":"#d8d5f0",
        "btn_danger":    "#fca5a5",
        "btn_danger_h":  "#f87171",
        "success":       "#059669",
        "warning":       "#d97706",
        "danger":        "#dc2626",
        "border":        "#d4d2e8",
        "border_accent": "#7c3aed",
        "scrollbar":     "#7c3aed",
        "overlay":       "#f0eff8cc",
        "bar_track":     "#ddd6fe",
        "bar_fill":      "#7c3aed",
        "bar_fill_low":  "#dc2626",
        "separator":     "#d4d2e8",
    },

    # ---- Sepia — warm parchment with amber accents ----
    "sepia": {
        "bg_primary":    "#1e1610",
        "bg_secondary":  "#27201a",
        "bg_panel":      "#2e2518",
        "bg_card":       "#352b1c",
        "bg_input":      "#1a1308",
        "accent":        "#c49a3c",
        "accent_hover":  "#d4aa50",
        "accent_dark":   "#a07830",
        "accent_glow":   "#c49a3c44",
        "text_primary":  "#f0e0c0",
        "text_secondary":"#c8a870",
        "text_muted":    "#806040",
        "text_accent":   "#e0c080",
        "choice_bg":     "#352b1c",
        "choice_hover":  "#453520",
        "choice_border": "#c49a3c",
        "btn_primary":   "#c49a3c",
        "btn_primary_h": "#d4aa50",
        "btn_secondary": "#3a2e1e",
        "btn_secondary_h":"#4a3c28",
        "btn_danger":    "#7f2020",
        "btn_danger_h":  "#962828",
        "success":       "#6ab04c",
        "warning":       "#e6a817",
        "danger":        "#c0392b",
        "border":        "#4a3820",
        "border_accent": "#c49a3c",
        "scrollbar":     "#c49a3c",
        "overlay":       "#1e1610cc",
        "bar_track":     "#4a3820",
        "bar_fill":      "#c49a3c",
        "bar_fill_low":  "#c0392b",
        "separator":     "#4a3820",
    },
}

# ---------------------------------------------------------------------------
# Fonts
# The story / passage text uses a serif face for immersion.
# All UI chrome uses Segoe UI (always present on Win 10/11).
# ---------------------------------------------------------------------------

STORY_FONT_FAMILY = "Georgia"   # lovely serif, ships with Windows
UI_FONT_FAMILY    = "Segoe UI"  # crisp sans-serif system font

FONTS: dict[str, tuple] = {
    # Story text
    "story":         (STORY_FONT_FAMILY, 14),
    "story_large":   (STORY_FONT_FAMILY, 16),
    "story_small":   (STORY_FONT_FAMILY, 12),
    "story_italic":  (STORY_FONT_FAMILY, 14, "italic"),

    # Headings
    "title":         (STORY_FONT_FAMILY, 40, "bold"),
    "title_sub":     (STORY_FONT_FAMILY, 16, "italic"),
    "heading":       (UI_FONT_FAMILY,    22, "bold"),
    "subheading":    (UI_FONT_FAMILY,    15, "bold"),
    "chapter":       (STORY_FONT_FAMILY, 13, "italic"),

    # UI / chrome
    "ui":            (UI_FONT_FAMILY, 12),
    "ui_small":      (UI_FONT_FAMILY, 10),
    "ui_large":      (UI_FONT_FAMILY, 14),
    "ui_bold":       (UI_FONT_FAMILY, 12, "bold"),
    "choice":        (UI_FONT_FAMILY, 13),
    "choice_num":    (UI_FONT_FAMILY, 11),
    "btn":           (UI_FONT_FAMILY, 13, "bold"),
    "label":         (UI_FONT_FAMILY, 11),
    "stat_value":    (UI_FONT_FAMILY, 16, "bold"),
}


def get_story_font(size: int) -> tuple:
    """Return a story font tuple at the requested point size."""
    return (STORY_FONT_FAMILY, size)


def get_ui_font(size: int, weight: str = "normal") -> tuple:
    """Return a UI font tuple."""
    if weight == "bold":
        return (UI_FONT_FAMILY, size, "bold")
    return (UI_FONT_FAMILY, size)
