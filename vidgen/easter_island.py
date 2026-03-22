#!/usr/bin/env python3
"""Easter Island 'Walking Statues' TikTok — v7 Professional Upgrade.

Engine features used:
  - Camera system: zoom punches, shake, emphasis flash
  - Cross-dissolve transitions between all scenes
  - Kinetic typography: char_slam on hook, char_pop on payoff
  - Color grading: warm cinematic look
  - Progress bar: gold, top position
  - Sound design: ambient pad + whoosh/impact SFX
  - Ken Burns / drift backgrounds

Total: ~29s. Mystery/reveal arc.
"""

import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from vidgen import render_video, preview_frame

ASSETS = "assets"
SFX = "assets/sfx"

TTS_SCRIPT = """For decades, scientists said Easter Island's statues were dragged on wooden sleds.
But there's a problem. The island had almost no trees.
The Rapa Nui people always had a different answer. The statues walked.
In 2011, archaeologists tested it. 18 people. 3 ropes. A 5-ton replica. It walked.
887 statues. Moved up to 18 km. All by walking.
The Rapa Nui told us the truth for centuries. We just didn't listen."""

screenplay = {
    "title": "How Easter Island's Statues Walked",
    "resolution": [1080, 1920],
    "fps": 30,
    "audio": "tts_narration_v5.mp3",

    # --- NEW: Cinematic color grading ---
    "color_grade": {
        "contrast": 1.12,
        "saturation": 0.88,
        "warmth": 0.04,
        "black_point": 8,
    },

    # --- NEW: Progress bar ---
    "progress_bar": {
        "position": "top",
        "color": "#FFD700",
        "height": 3,
        "background": "#FFFFFF15",
    },

    # Sound design — SFX disabled per feedback
    # "sound_design": { ... },

    "scenes": [

        # ============================================================
        # Scene 1: THE WRONG ANSWER (0-4.5s)
        # ============================================================
        {
            "duration": 4.5,
            "background": f"{ASSETS}/moai_row.jpg",
            "bg_animation": "ken_burns",
            "kb_direction": "right",
            "kb_zoom": [1.0, 1.12],
            "vignette": True,
            "camera": {
                "zoom_punches": [
                    {"time": 0.3, "zoom": 1.04, "duration": 0.25, "ease_back": 0.6},
                ],
                "shakes": [
                    {"time": 0.3, "intensity": 4, "duration": 0.2},
                ],
                "flashes": [
                    {"time": 0.3, "opacity": 0.10, "duration": 0.08},
                ],
            },
            "layers": [
                {
                    "type": "shape", "shape": "rectangle",
                    "position": [0, 0], "size": [1080, 1920],
                    "color": "#00000035", "animation": "none",
                },
                # Hook — char_slam for energy
                {
                    "type": "text",
                    "content": "They were DRAGGED.",
                    "font": "BebasNeue", "size": 130,
                    "color": "#FFD700",
                    "position": [540, 700], "anchor": "mm",
                    "animation": "char_slam",
                    "char_stagger": 0.025,
                    "anim_duration": 0.6,
                    "shadow": {"color": "#000000", "x": 4, "y": 4},
                },
                {
                    "type": "shape", "shape": "line",
                    "position": [240, 780], "size": [600, 0],
                    "color": "#FFD700", "width": 3,
                    "animation": "wipe_right", "anim_duration": 0.8, "delay": 0.4,
                },
                {
                    "type": "text",
                    "content": "Scientists said they were",
                    "font": "Inter-Bold", "size": 48,
                    "color": "#FFFFFF",
                    "position": [540, 900], "anchor": "mm",
                    "animation": "fade_in", "anim_duration": 0.8, "delay": 0.8,
                    "stroke_width": 2, "stroke_color": "#000000",
                },
                {
                    "type": "text",
                    "content": "dragged on wooden sleds.",
                    "font": "Inter-Bold", "size": 48,
                    "color": "#CCCCCC",
                    "position": [540, 970], "anchor": "mm",
                    "animation": "slide_up", "anim_duration": 0.5, "delay": 1.4,
                    "stroke_width": 2, "stroke_color": "#000000",
                },
            ],
            "transition": "cross_dissolve",
            "transition_duration": 0.4,
        },

        # ============================================================
        # Scene 2: THE CONTRADICTION (4.5-9s)
        # ============================================================
        {
            "duration": 4.5,
            "background": f"{ASSETS}/moai_hillside.jpg",
            "bg_animation": "drift",
            "vignette": True,
            "camera": {
                "zoom_punches": [
                    {"time": 0.9, "zoom": 1.05, "duration": 0.3, "ease_back": 0.7},
                ],
                "shakes": [
                    {"time": 0.9, "intensity": 5, "duration": 0.25},
                ],
                "flashes": [
                    {"time": 0.9, "opacity": 0.08, "duration": 0.06},
                ],
            },
            "layers": [
                {
                    "type": "shape", "shape": "rectangle",
                    "position": [0, 0], "size": [1080, 1920],
                    "color": "#00000030", "animation": "none",
                },
                {
                    "type": "shape", "shape": "rectangle",
                    "position": [0, 0], "size": [1080, 440],
                    "color": "#000000BB", "animation": "none",
                },
                {
                    "type": "text",
                    "content": "But there's a problem.",
                    "font": "Inter-Bold", "size": 56,
                    "color": "#FF4444",
                    "position": [540, 180], "anchor": "mm",
                    "animation": "fade_in", "anim_duration": 0.5, "delay": 0.3,
                    "stroke_width": 2, "stroke_color": "#000000",
                },
                # Slam with highlight wipe
                {
                    "type": "text",
                    "content": "Almost no trees.",
                    "font": "Inter-Bold", "size": 60,
                    "color": "#FFFFFF",
                    "position": [540, 280], "anchor": "mm",
                    "animation": "slam", "anim_duration": 0.4, "delay": 0.9,
                    "stroke_width": 2, "stroke_color": "#000000",
                    "bg_color": "#FF444466",
                    "bg_animation": "wipe_right",
                    "bg_anim_duration": 0.3,
                    "bg_padding": [20, 10],
                },
            ],
            "transition": "cross_dissolve",
            "transition_duration": 0.4,
        },

        # ============================================================
        # Scene 3: THE ORAL TRADITION (9-14s)
        # ============================================================
        {
            "duration": 5.0,
            "background": f"{ASSETS}/moai_painting.jpg",
            "bg_animation": "ken_burns",
            "kb_direction": "left",
            "kb_zoom": [1.0, 1.10],
            "vignette": True,
            "camera": {
                "zoom_punches": [
                    {"time": 1.0, "zoom": 1.03, "duration": 0.3, "ease_back": 0.8},
                ],
            },
            "layers": [
                {
                    "type": "shape", "shape": "rectangle",
                    "position": [0, 1400], "size": [1080, 520],
                    "color": "#000000DD", "animation": "none",
                },
                {
                    "type": "text",
                    "content": "The Rapa Nui always said:",
                    "font": "DMSerifDisplay", "size": 52,
                    "color": "#FFFFFF",
                    "position": [540, 1560], "anchor": "mm",
                    "animation": "fade_in", "anim_duration": 0.6, "delay": 0.3,
                    "stroke_width": 2, "stroke_color": "#000000",
                },
                {
                    "type": "text",
                    "content": "The statues walked.",
                    "font": "DMSerifDisplay", "size": 64,
                    "color": "#FFD700",
                    "position": [540, 1660], "anchor": "mm",
                    "animation": "char_pop",
                    "char_stagger": 0.04,
                    "anim_duration": 0.8, "delay": 1.0,
                    "stroke_width": 2, "stroke_color": "#000000",
                    "shadow": {"color": "#000000", "x": 3, "y": 3},
                },
            ],
            "transition": "cross_dissolve",
            "transition_duration": 0.4,
        },

        # ============================================================
        # Scene 4: THE PROOF (14-19s) — PAYOFF
        # ============================================================
        {
            "duration": 5.0,
            "background": f"{ASSETS}/walking_technique.png",
            "bg_animation": "drift",
            "camera": {
                "zoom_punches": [
                    {"time": 2.0, "zoom": 1.06, "duration": 0.25, "ease_back": 0.5},
                ],
                "shakes": [
                    {"time": 2.0, "intensity": 7, "duration": 0.3},
                ],
                "flashes": [
                    {"time": 2.0, "opacity": 0.15, "duration": 0.1},
                ],
            },
            "layers": [
                {
                    "type": "text",
                    "content": "In 2011, they tested it.",
                    "font": "Inter-Bold", "size": 52,
                    "color": "#FFFFFF",
                    "position": [540, 780], "anchor": "mm",
                    "animation": "fade_in", "anim_duration": 0.4, "delay": 0.2,
                    "stroke_width": 2, "stroke_color": "#000000",
                },
                {
                    "type": "text",
                    "content": "18 people. 3 ropes.",
                    "font": "Inter-Bold", "size": 56,
                    "color": "#FFFFFF",
                    "position": [540, 870], "anchor": "mm",
                    "animation": "pop", "anim_duration": 0.4, "delay": 0.7,
                    "stroke_width": 2, "stroke_color": "#000000",
                },
                {
                    "type": "text",
                    "content": "A 5-ton replica.",
                    "font": "Inter-Bold", "size": 56,
                    "color": "#FFFFFF",
                    "position": [540, 950], "anchor": "mm",
                    "animation": "pop", "anim_duration": 0.4, "delay": 1.2,
                    "stroke_width": 2, "stroke_color": "#000000",
                },
                # THE payoff — char_slam for maximum impact
                {
                    "type": "text",
                    "content": "IT WALKED.",
                    "font": "BebasNeue", "size": 120,
                    "color": "#FFD700",
                    "position": [540, 1100], "anchor": "mm",
                    "animation": "char_slam",
                    "char_stagger": 0.03,
                    "anim_duration": 0.5, "delay": 2.0,
                    "shadow": {"color": "#000000", "x": 5, "y": 5},
                },
            ],
            "transition": "cross_dissolve",
            "transition_duration": 0.4,
        },

        # ============================================================
        # Scene 5: THE SCALE (19-23.5s)
        # ============================================================
        {
            "duration": 4.5,
            "background": f"{ASSETS}/easter_island_map.png",
            "bg_animation": "ken_burns",
            "kb_direction": "down",
            "kb_zoom": [1.0, 1.08],
            "vignette": True,
            "camera": {
                "zoom_punches": [
                    {"time": 0.2, "zoom": 1.04, "duration": 0.3, "ease_back": 0.6},
                ],
                "shakes": [
                    {"time": 0.2, "intensity": 4, "duration": 0.2},
                ],
            },
            "layers": [
                {
                    "type": "shape", "shape": "rectangle",
                    "position": [0, 0], "size": [1080, 500],
                    "color": "#000000DD", "animation": "none",
                },
                {
                    "type": "text",
                    "content": "887 STATUES",
                    "font": "BebasNeue", "size": 110,
                    "color": "#FFD700",
                    "position": [540, 160], "anchor": "mm",
                    "animation": "char_slam",
                    "char_stagger": 0.02,
                    "anim_duration": 0.5, "delay": 0.2,
                    "shadow": {"color": "#000000", "x": 3, "y": 3},
                },
                {
                    "type": "text",
                    "content": "Moved up to 18 km.",
                    "font": "Inter-Bold", "size": 48,
                    "color": "#FFFFFF",
                    "position": [540, 300], "anchor": "mm",
                    "animation": "fade_in", "anim_duration": 0.5, "delay": 0.8,
                    "stroke_width": 2, "stroke_color": "#000000",
                },
                {
                    "type": "text",
                    "content": "All by walking.",
                    "font": "Inter-Bold", "size": 52,
                    "color": "#FFD700",
                    "position": [540, 380], "anchor": "mm",
                    "animation": "char_wave",
                    "char_stagger": 0.04,
                    "anim_duration": 0.6, "delay": 1.4,
                    "stroke_width": 2, "stroke_color": "#000000",
                },
            ],
            "transition": "cross_dissolve",
            "transition_duration": 0.4,
        },

        # ============================================================
        # Scene 6: THE PUNCH (23.5-29s)
        # ============================================================
        {
            "duration": 6.7,
            "background": f"{ASSETS}/moai_quarry_v3.jpg",
            "bg_animation": "ken_burns",
            "kb_direction": "up",
            "kb_zoom": [1.0, 1.10],
            "vignette": True,
            "letterbox": 0.03,
            "layers": [
                {
                    "type": "shape", "shape": "rectangle",
                    "position": [0, 900], "size": [1080, 1020],
                    "color": "#00000088", "animation": "none",
                },
                {
                    "type": "shape", "shape": "line",
                    "position": [290, 1020], "size": [500, 0],
                    "color": "#FFD700", "width": 2,
                    "animation": "wipe_right", "anim_duration": 1.0, "delay": 0.3,
                },
                {
                    "type": "text",
                    "content": "The Rapa Nui told us",
                    "font": "DMSerifDisplay", "size": 58,
                    "color": "#FFFFFF",
                    "position": [540, 1100], "anchor": "mm",
                    "animation": "fade_in", "anim_duration": 0.8, "delay": 0.3,
                    "stroke_width": 2, "stroke_color": "#000000",
                },
                {
                    "type": "text",
                    "content": "the truth for centuries.",
                    "font": "DMSerifDisplay", "size": 58,
                    "color": "#FFD700",
                    "position": [540, 1190], "anchor": "mm",
                    "animation": "fade_in", "anim_duration": 0.8, "delay": 0.8,
                    "stroke_width": 2, "stroke_color": "#000000",
                },
                {
                    "type": "shape", "shape": "line",
                    "position": [290, 1250], "size": [500, 0],
                    "color": "#FFD700", "width": 2,
                    "animation": "wipe_right", "anim_duration": 1.0, "delay": 1.5,
                },
                # Quiet closer
                {
                    "type": "text",
                    "content": "We just didn't listen.",
                    "font": "DMSerifDisplay", "size": 50,
                    "color": "#AAAAAA",
                    "position": [540, 1360], "anchor": "mm",
                    "animation": "fade_in", "anim_duration": 1.2, "delay": 2.2,
                    "stroke_width": 1, "stroke_color": "#000000",
                },
            ],
            "transition": "cross_dissolve",
            "transition_duration": 0.6,
        },
    ],
}


if __name__ == "__main__":
    # Preview key frames
    previews = [
        (2.0, "1_wrong_answer"),
        (6.5, "2_contradiction"),
        (11.5, "3_oral_tradition"),
        (16.5, "4_proof"),
        (21.5, "5_scale"),
        (26.5, "6_punch"),
    ]
    for t, label in previews:
        f = preview_frame(screenplay, t, f"preview_v7_{label}.png")
        print(f"Preview {label} @ {t}s saved")

    # Render full video
    render_video(screenplay, "easter_island_v15.mp4")
