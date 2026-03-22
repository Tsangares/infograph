#!/usr/bin/env python3
"""Finish the Course Is Wrong — FULL REBUILD with zone layout.

6 scenes, ~61.0s (58.0s audio + 3s hold).
Domain shapes: pathway_track, student_fig, filter_funnel, pie_wedge.
Uses safe_place() + validate_layout() per PRODUCTION_GUIDE.

VTT cues (absolute → relative):
  Scene 1 (0.0–7.8s):   0.30 same order... 3.72 algebra geometry... 7.78 set in 1894
  Scene 2 (7.8–18.3s):  12.44 colleges want... 15.92 filtered out... 18.34 only 5%
  Scene 3 (18.3–28.0s): 22.46 statistics... 24.68 probability... 26.90 skip all of it
  Scene 4 (28.0–38.1s): 28.34 1894 not designed... 32.16 filter... 35.32 funnel
  Scene 5 (38.1–49.2s): 39.94 millions take calculus... 42.96 while probability...
  Scene 6 (49.2–61.0s): 49.20 not because it works... 53.36 because it's 1894
"""

import json, os, sys, subprocess, shutil
from pathlib import Path

VENV_PYTHON = Path(__file__).parent / ".venv" / "bin" / "python3"
if not sys.prefix.startswith(str(Path(__file__).parent / ".venv")):
    os.execv(str(VENV_PYTHON), [str(VENV_PYTHON), __file__] + sys.argv[1:])

os.chdir(os.path.dirname(os.path.abspath(__file__)))

from manim import *
import numpy as np

config.pixel_width = 1080
config.pixel_height = 1920
config.frame_rate = 30
config.frame_width = 9
config.frame_height = 16
config.background_color = "#080A10"
config.disable_caching = True

BG = "#080A10"; GRID_COL = "#1A2030"; SURFACE = "#15192A"
TRACK_GRAY = "#374151"; AGED_RUST = "#8B6914"
FILTER_RED = "#EF4444"; BRANCH_GOLD = "#FFD700"; GOLD_DIM = "#B8960F"
STATS_BLUE = "#3B82F6"; DIM = "#4A5568"; CHECK_GREEN = "#22C55E"
WHITE_SOFT = "#F0F0F0"; MUTED = "#7B8DA0"

SAFE_W = 8.0; SAFE_TOP = 7.2; SAFE_BOT = -6.4
ZONE_TITLE = 6.2; ZONE_UPPER = 3.5; ZONE_MID = 0.0
ZONE_LOWER = -3.5; ZONE_FOOTER = -6.0

def gradient_bg():
    bg = Rectangle(width=12, height=20, fill_color=BG, fill_opacity=1, stroke_width=0)
    glow = Circle(radius=5, fill_color="#121828", fill_opacity=0.08, stroke_width=0).move_to(UP*2)
    return VGroup(bg, glow)

def grid_lines(op=0.04):
    lines = VGroup()
    for i in range(13):
        y = -8 + i*16/12
        lines.add(Line(LEFT*5, RIGHT*5, color=GRID_COL, stroke_width=0.5).move_to(UP*y).set_opacity(op))
    for j in range(7):
        x = -4.5 + j*9/6
        lines.add(Line(DOWN*8, UP*8, color=GRID_COL, stroke_width=0.5).move_to(RIGHT*x).set_opacity(op))
    return lines

def safe_text(c, **kw):
    t = Text(c, **kw)
    if t.width > SAFE_W: t.scale(SAFE_W/t.width)
    return t

_ZONES = {"TITLE":ZONE_TITLE,"UPPER":ZONE_UPPER,"MID":ZONE_MID,"LOWER":ZONE_LOWER,"FOOTER":ZONE_FOOTER}
def safe_place(mob, zone, x=0):
    y = _ZONES[zone] if isinstance(zone, str) else float(zone)
    mob.move_to(np.array([float(x), y, 0]))
    if mob.width > SAFE_W: mob.scale(SAFE_W/mob.width)
    if mob.get_top()[1] > SAFE_TOP: mob.shift(DOWN*(mob.get_top()[1]-SAFE_TOP))
    if mob.get_bottom()[1] < SAFE_BOT: mob.shift(UP*(SAFE_BOT-mob.get_bottom()[1]))
    return mob

def validate_layout(sc):
    ys = [m.get_center()[1] for m in sc.mobjects[2:] if hasattr(m,'get_center') and m.width>0.01]
    if ys and min(ys) > -1.5:
        print(f"  LAYOUT WARN: lowest y={min(ys):.1f}")

def label_pill(txt, color=BRANCH_GOLD, bg=SURFACE, fs=24):
    t = Text(txt, font="Inter", font_size=fs, color=color, weight="BOLD")
    if t.width > 3.0: t.scale(3.0/t.width)
    p = RoundedRectangle(width=t.width+0.3, height=t.height+0.2, corner_radius=0.1,
                         fill_color=bg, fill_opacity=0.9, stroke_width=0).move_to(t)
    return VGroup(p, t)

# Domain shapes
def pathway_track(w=6, y=0, col=TRACK_GRAY, stations=None):
    tr = Line(LEFT*w/2, RIGHT*w/2, color=col, stroke_width=4).move_to(UP*y)
    g = VGroup(tr)
    if stations:
        for i, nm in enumerate(stations):
            x = -w/2 + (i+1)*w/(len(stations)+1)
            g.add(Dot(np.array([x,y,0]), radius=0.1, color=col))
            p = label_pill(nm, color=WHITE_SOFT, fs=18); p.move_to(np.array([x,y+0.5,0]))
            g.add(p)
    return g

def student_fig(col=WHITE_SOFT, h=0.7):
    hd = Circle(radius=h*0.12, fill_color=col, fill_opacity=0.8, stroke_width=0).move_to(UP*h*0.3)
    bd = Rectangle(width=h*0.18, height=h*0.45, fill_color=col, fill_opacity=0.6, stroke_width=0)
    return VGroup(hd, bd).scale_to_fit_height(h)

def filter_funnel(wt=5, wb=1.2, h=7, col=FILTER_RED):
    return Polygon(np.array([-wt/2,h/2,0]),np.array([wt/2,h/2,0]),
                   np.array([wb/2,-h/2,0]),np.array([-wb/2,-h/2,0]),
                   fill_color=col, fill_opacity=0.1, stroke_color=col, stroke_width=2)

def pie_wedge(ang=18, r=2, col=BRANCH_GOLD):
    ar = ang*PI/180
    f = Arc(radius=r, start_angle=PI/2, angle=-ar, color=col, fill_opacity=0.6, stroke_width=0)
    a = Arc(radius=r, start_angle=PI/2, angle=-ar, color=col, stroke_width=2)
    l1 = Line(ORIGIN, UP*r, color=col, stroke_width=2)
    l2 = Line(ORIGIN, np.array([r*np.sin(ar), r*np.cos(ar), 0]), color=col, stroke_width=2)
    return VGroup(f, a, l1, l2)


class Scene1_Hook(Scene):
    DURATION = 7.4
    def construct(self):
        self.add(gradient_bg(), grid_lines())
        t = 0
        pill = label_pill("THE SEQUENCE", color=MUTED, fs=22); safe_place(pill, "TITLE")
        track = pathway_track(6, ZONE_UPPER, TRACK_GRAY, ["ALG","GEO","ALG 2","CALC"])
        fig = student_fig(WHITE_SOFT, 0.8); fig.move_to(LEFT*3+UP*(ZONE_UPPER-0.8))
        date = safe_text("1894", font="Bebas Neue", font_size=140, color=GOLD_DIM); date.set_opacity(0.5)
        safe_place(date, "LOWER")
        ctx = safe_text("130 years. Same order.", font="Inter", font_size=26, color=DIM, weight="BOLD")
        safe_place(ctx, "FOOTER")
        self.play(FadeIn(pill), run_time=0.3); t += 0.3
        self.play(Create(track[0]), run_time=0.5); t += 0.5
        self.play(LaggedStart(*[FadeIn(track[i]) for i in range(1,len(track))], lag_ratio=0.08), run_time=0.6); t += 0.6
        self.play(FadeIn(fig, shift=UP*0.2), run_time=0.4); t += 0.4
        self.wait(3.5); t += 3.5
        self.play(FadeIn(date, scale=1.1), run_time=0.6); t += 0.6
        self.play(Flash(date.get_center(), color=GOLD_DIM, line_length=0.4, num_lines=8, run_time=0.3)); t += 0.3
        self.play(FadeIn(ctx, shift=UP*0.04), run_time=0.4); t += 0.4
        target = getattr(self.__class__, 'DURATION', 7.4)
        self.wait(max(0.1, target - t - 0.3))
        validate_layout(self)

class Scene2_WrongAnswer(Scene):
    DURATION = 10.0
    def construct(self):
        self.add(gradient_bg(), grid_lines())
        t = 0
        pill = label_pill("THE WRONG ANSWER", color=FILTER_RED, fs=22); safe_place(pill, "TITLE")
        track = pathway_track(6, ZONE_UPPER, TRACK_GRAY, ["ALG","GEO","ALG 2","CALC"])
        star = Polygon(*[np.array([0.3*np.cos(PI/2+i*2*PI/5),0.3*np.sin(PI/2+i*2*PI/5),0])
                         if i%2==0 else np.array([0.15*np.cos(PI/2+i*2*PI/5),0.15*np.sin(PI/2+i*2*PI/5),0])
                         for i in range(10)], fill_color=BRANCH_GOLD, fill_opacity=0.8, stroke_width=0
                       ).move_to(RIGHT*3+UP*ZONE_UPPER)
        students = VGroup(*[student_fig(WHITE_SOFT, 0.5).move_to(LEFT*3+RIGHT*i*0.3+UP*(ZONE_UPPER-0.6)) for i in range(8)])
        stat = safe_text("MOST DROP OUT", font="Bebas Neue", font_size=70, color=FILTER_RED); safe_place(stat, "MID")
        stat_sub = safe_text("BEFORE CALCULUS", font="Inter", font_size=28, color=DIM, weight="BOLD")
        stat_sub.next_to(stat, DOWN, buff=0.3)
        five_pct = safe_text("5%", font="Bebas Neue", font_size=120, color=FILTER_RED); safe_place(five_pct, "LOWER")
        of_jobs = safe_text("OF JOBS USE CALCULUS", font="Inter", font_size=28, color=DIM, weight="BOLD")
        of_jobs.next_to(five_pct, DOWN, buff=0.3)
        self.play(FadeIn(pill), run_time=0.3); t += 0.3
        self.add(track, star); self.play(FadeIn(students), run_time=0.3); t += 0.3
        self.play(students.animate.shift(RIGHT*1.2), run_time=0.6); t += 0.6
        self.play(students[0].animate.shift(DOWN*1.5).set_opacity(0),
                  students[1].animate.shift(DOWN*1.5).set_opacity(0), run_time=0.2)
        self.play(students.animate.shift(RIGHT*1.0), run_time=0.5); t += 0.5
        self.play(students[2].animate.shift(DOWN*1.5).set_opacity(0),
                  students[3].animate.shift(DOWN*1.5).set_opacity(0),
                  students[4].animate.shift(DOWN*1.5).set_opacity(0), run_time=0.2)
        self.play(students.animate.shift(RIGHT*1.0), run_time=0.5); t += 0.5
        self.play(students[5].animate.shift(DOWN*1.5).set_opacity(0), run_time=0.15); t += 0.15
        self.play(FadeIn(stat, scale=1.1), FadeIn(stat_sub), run_time=0.5); t += 0.5
        self.wait(4.5); t += 4.5
        self.play(FadeIn(five_pct, scale=1.2), run_time=0.5); t += 0.5
        self.play(Flash(five_pct.get_center(), color=FILTER_RED, line_length=0.4, num_lines=8, run_time=0.3)); t += 0.3
        self.play(FadeIn(of_jobs), run_time=0.3); t += 0.3
        target = getattr(self.__class__, 'DURATION', 10.0)
        self.wait(max(0.1, target - t - 0.3))
        validate_layout(self)

class Scene3_Contradiction(Scene):
    DURATION = 9.2
    def construct(self):
        self.add(gradient_bg(), grid_lines())
        t = 0
        pill = label_pill("THE CONTRADICTION", color=STATS_BLUE, fs=22); safe_place(pill, "TITLE")
        pie = Circle(radius=1.8, stroke_color=DIM, stroke_width=2, fill_opacity=0).move_to(UP*ZONE_UPPER)
        wedge = pie_wedge(18, 1.8, BRANCH_GOLD).move_to(pie)
        pct = safe_text("5%", font="Bebas Neue", font_size=50, color=BRANCH_GOLD)
        pct.next_to(pie, RIGHT, buff=0.4)
        pct_lbl = safe_text("CALCULUS", font="Inter", font_size=20, color=BRANCH_GOLD, weight="BOLD")
        pct_lbl.next_to(pct, DOWN, buff=0.1)
        useful = VGroup(); strikes = VGroup()
        for txt, y in [("STATISTICS",ZONE_MID+1),("PROBABILITY",ZONE_MID),("DATA",ZONE_MID-1)]:
            lbl = safe_text(txt, font="Bebas Neue", font_size=50, color=STATS_BLUE).move_to(UP*y)
            useful.add(lbl)
            strikes.add(Line(lbl.get_left()+LEFT*0.2, lbl.get_right()+RIGHT*0.2, color=FILTER_RED, stroke_width=3).move_to(lbl))
        skip = safe_text("WE SKIP ALL OF IT.", font="Bebas Neue", font_size=55, color=FILTER_RED); safe_place(skip, "LOWER")
        cost = safe_text("Every decision. Every dollar.", font="Inter", font_size=24, color=DIM, weight="BOLD"); safe_place(cost, "FOOTER")
        self.play(FadeIn(pill), run_time=0.3); t += 0.3
        self.play(Create(pie), run_time=0.3); t += 0.3
        self.play(GrowFromCenter(wedge), FadeIn(pct), FadeIn(pct_lbl), run_time=0.5); t += 0.5
        self.wait(2.4); t += 2.4
        self.play(LaggedStart(*[FadeIn(u, shift=LEFT*0.2) for u in useful], lag_ratio=0.15), run_time=0.6); t += 0.6
        self.wait(2.5); t += 2.5
        self.play(LaggedStart(*[Create(s) for s in strikes], lag_ratio=0.15), run_time=0.5); t += 0.5
        self.wait(1.0); t += 1.0
        self.play(FadeIn(skip, scale=1.1), run_time=0.4); t += 0.4
        self.play(Flash(skip.get_center(), color=FILTER_RED, line_length=0.3, num_lines=8, run_time=0.2)); t += 0.2
        self.play(FadeIn(cost, shift=UP*0.04), run_time=0.3); t += 0.3
        target = getattr(self.__class__, 'DURATION', 9.2)
        self.wait(max(0.1, target - t - 0.3))
        validate_layout(self)

class Scene4_Proof(Scene):
    DURATION = 9.6
    def construct(self):
        self.add(gradient_bg(), grid_lines())
        t = 0
        pill = label_pill("THE PROOF", color=FILTER_RED, fs=22); safe_place(pill, "TITLE")
        funnel = filter_funnel(5.5, 1.2, 10, FILTER_RED); funnel.move_to(UP*0.5)
        station_pills = VGroup()
        for nm, y in [("ALG",4),("GEO",2),("ALG 2",0),("CALC",-2)]:
            p = label_pill(nm, color=WHITE_SOFT, fs=16); p.move_to(LEFT*2+UP*y)
            station_pills.add(p)
        np.random.seed(4)
        studs = VGroup(*[student_fig(WHITE_SOFT, 0.6).move_to(np.array([np.random.uniform(-1.5,1.5),5.5,0])) for _ in range(8)])
        college = RoundedRectangle(width=2, height=0.6, corner_radius=0.1, fill_color=SURFACE, fill_opacity=0.9,
                                   stroke_color=BRANCH_GOLD, stroke_width=1.5).move_to(DOWN*5)
        college_lbl = safe_text("COLLEGE", font="Inter", font_size=20, color=BRANCH_GOLD, weight="BOLD").move_to(college)
        date = safe_text("1894", font="Bebas Neue", font_size=60, color=GOLD_DIM); date.set_opacity(0.4); safe_place(date, "FOOTER", x=-1.5)
        feat = safe_text("A FILTER.", font="Bebas Neue", font_size=50, color=FILTER_RED); safe_place(feat, "FOOTER", x=1.5)
        self.play(FadeIn(pill), run_time=0.3); t += 0.3
        self.play(DrawBorderThenFill(funnel), run_time=0.7); t += 0.7
        self.play(LaggedStart(*[FadeIn(p) for p in station_pills], lag_ratio=0.1), run_time=0.4); t += 0.4
        self.play(LaggedStart(*[FadeIn(s, shift=DOWN*0.5) for s in studs], lag_ratio=0.04), run_time=0.4); t += 0.4
        self.wait(1.5); t += 1.5
        for i in range(6):
            d = LEFT if i%2==0 else RIGHT
            self.play(studs[i].animate.shift(d*2.5+DOWN).set_opacity(0), run_time=0.12); t += 0.12
        self.play(FadeIn(VGroup(college, college_lbl), shift=UP*0.2), run_time=0.3); t += 0.3
        self.play(studs[6].animate.move_to(college.get_center()+LEFT*0.3),
                  studs[7].animate.move_to(college.get_center()+RIGHT*0.3), run_time=0.4)
        self.wait(3.0); t += 3.0
        self.play(FadeIn(date), FadeIn(feat, scale=1.1), run_time=0.5); t += 0.5
        target = getattr(self.__class__, 'DURATION', 9.6)
        self.wait(max(0.1, target - t - 0.3))
        validate_layout(self)

class Scene5_Scale(Scene):
    DURATION = 10.5
    def construct(self):
        self.add(gradient_bg(), grid_lines())
        t = 0
        pill = label_pill("THE SCALE", color=BRANCH_GOLD, fs=22); safe_place(pill, "TITLE")
        mf = filter_funnel(2.5, 0.6, 4, FILTER_RED); mf.scale(0.5).move_to(LEFT*2.5+UP*(ZONE_UPPER+0.5))
        cnt = safe_text("3M", font="Bebas Neue", font_size=50, color="#FF6B6B").move_to(LEFT*2.5+UP*(ZONE_UPPER-1.0))
        wl = safe_text("WASTED", font="Inter", font_size=20, color="#FF6B6B", weight="BOLD"); wl.next_to(cnt, DOWN, buff=0.15)
        mp = Line(RIGHT*0.5, RIGHT*2.5, color=TRACK_GRAY, stroke_width=3).move_to(RIGHT*1.5+UP*(ZONE_UPPER+0.5))
        branches = VGroup()
        for nm, col, ang in [("STATS",STATS_BLUE,-20),("PROB",BRANCH_GOLD,0),("FINANCE",CHECK_GREEN,20)]:
            end = mp.get_right()+np.array([1.5*np.cos(ang*PI/180), 1.5*np.sin(-ang*PI/180), 0])
            branches.add(Line(mp.get_right(), end, color=col, stroke_width=2.5))
            lb = label_pill(nm, color=col, fs=14); lb.move_to(end+DOWN*0.3); branches.add(lb)
        div = DashedLine(UP*2.0, DOWN*2.0, color=MUTED, stroke_width=1, dash_length=0.15); safe_place(div, "LOWER", x=0)
        fl = safe_text("MOST FAIL", font="Bebas Neue", font_size=50, color=FILTER_RED).move_to(LEFT*2.5+UP*ZONE_LOWER)
        ps = safe_text("ALL BENEFIT", font="Bebas Neue", font_size=45, color=CHECK_GREEN).move_to(RIGHT*2+UP*ZONE_LOWER)
        bs = VGroup(*[student_fig(BRANCH_GOLD, 0.5).move_to(RIGHT*(0.5+i*0.5)+UP*(ZONE_MID-0.5)) for i in range(6)])
        alt = safe_text("ALTERNATIVE EXISTS.", font="Bebas Neue", font_size=45, color=BRANCH_GOLD); safe_place(alt, "FOOTER")
        self.play(FadeIn(pill), run_time=0.3); t += 0.3
        self.play(FadeIn(mf), FadeIn(cnt, scale=1.1), FadeIn(wl), run_time=0.5); t += 0.5
        self.wait(3.7); t += 3.7
        self.play(Create(mp), run_time=0.3); t += 0.3
        self.play(LaggedStart(*[Create(b) if isinstance(b, Line) else FadeIn(b) for b in branches], lag_ratio=0.08), run_time=0.6); t += 0.6
        self.play(LaggedStart(*[FadeIn(s, shift=UP*0.15) for s in bs], lag_ratio=0.05), run_time=0.4); t += 0.4
        self.play(Create(div), run_time=0.2); t += 0.2
        self.play(FadeIn(fl), FadeIn(ps), run_time=0.4); t += 0.4
        self.wait(2.5); t += 2.5
        self.play(FadeIn(alt, scale=1.08), run_time=0.4); t += 0.4
        self.play(Flash(alt.get_center(), color=BRANCH_GOLD, line_length=0.3, num_lines=6, run_time=0.2)); t += 0.2
        target = getattr(self.__class__, 'DURATION', 10.5)
        self.wait(max(0.1, target - t - 0.3))
        validate_layout(self)

class Scene6_Punch(Scene):
    DURATION = 11.2
    def construct(self):
        self.add(gradient_bg())
        t = 0
        bh = 1.2
        self.add(Rectangle(width=12, height=bh, fill_color=BLACK, fill_opacity=1, stroke_width=0).to_edge(UP, buff=0),
                 Rectangle(width=12, height=bh, fill_color=BLACK, fill_opacity=1, stroke_width=0).to_edge(DOWN, buff=0))
        track = pathway_track(6, ZONE_UPPER-1, AGED_RUST, ["ALG","GEO","ALG 2","CALC"])
        for m in track: m.set_opacity(0.9)
        cracks = VGroup(*[Line(np.array([x,ZONE_UPPER-0.85,0]), np.array([x+0.3,ZONE_UPPER-1.15,0]),
                               color="#C49A2A", stroke_width=2) for x in [-1.5, 0.5, 2.5]])
        d_old = safe_text("1894", font="Bebas Neue", font_size=100, color=GOLD_DIM); d_old.set_opacity(0.7); safe_place(d_old, "MID", x=-1.5)
        d_new = safe_text("2026", font="Bebas Neue", font_size=100, color=WHITE_SOFT); safe_place(d_new, "MID", x=1.5)
        verdict = safe_text("No one changed the calendar.", font="DM Serif Display", font_size=40, color=MUTED); safe_place(verdict, "LOWER")
        self.play(FadeIn(track), run_time=0.8); t += 0.8
        self.wait(1.2); t += 1.2
        self.play(FadeIn(d_old), run_time=0.6); t += 0.6
        self.wait(1.4); t += 1.4
        self.play(FadeIn(d_new, scale=1.1), run_time=0.6); t += 0.6
        self.play(LaggedStart(*[FadeIn(c) for c in cracks], lag_ratio=0.1), run_time=0.4); t += 0.4
        self.wait(1.5); t += 1.5
        self.play(FadeIn(verdict, shift=UP*0.04), run_time=0.6); t += 0.6
        target = getattr(self.__class__, 'DURATION', 11.2)
        self.wait(max(0.1, target - t - 0.8))
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=1.0); t += 1.0
        self.play(FadeIn(Rectangle(width=12, height=20, fill_color=BLACK, fill_opacity=1, stroke_width=0)), run_time=0.5); t += 0.5
        validate_layout(self)

SCENES = [Scene1_Hook, Scene2_WrongAnswer, Scene3_Contradiction, Scene4_Proof, Scene5_Scale, Scene6_Punch]

def render_single_scene(idx):
    config.output_file = f"finish_the_course_scene_{idx+1}"
    config.media_dir = str(Path(__file__).parent / "media")
    SCENES[idx]().render()
    for mp4 in Path(config.media_dir).rglob(f"finish_the_course_scene_{idx+1}.mp4"):
        print(f"SCENE_FILE:{mp4}"); return

def render_previews():
    d = Path(__file__).parent / "previews"; d.mkdir(exist_ok=True)
    config.media_dir = str(Path(__file__).parent / "media")
    for i, S in enumerate(SCENES):
        n = f"finish_the_course_scene_{i+1}"; print(f"  Preview {n}...")
        config.output_file = n; config.save_last_frame = True; config.format = "png"
        S().render()
        for p in Path(config.media_dir).rglob(f"{n}*"):
            if p.suffix == ".png":
                dst = d / f"{n}.png"; shutil.copy2(str(p), str(dst))
                print(f"  OK: {dst} ({dst.stat().st_size//1024} KB)"); break
    config.save_last_frame = False; config.format = None

if __name__ == "__main__":
    import time, gc
    od = Path(__file__).parent
    if "--preview" in sys.argv:
        render_previews()
        try:
            from render_utils import run_preview_qa
            run_preview_qa(od / "previews")
        except ImportError: pass
        sys.exit(0)
    if "--scene" in sys.argv:
        timings_json = os.environ.get("TKK_SCENE_TIMINGS")
        if timings_json:
            _idx = int(sys.argv[sys.argv.index("--scene")+1])
            SCENES[_idx].DURATION = json.loads(timings_json)[_idx]
        render_single_scene(int(sys.argv[sys.argv.index("--scene")+1])); sys.exit(0)

    from render_utils import parallel_render_scenes, concat_scenes
    t0 = time.time()
    audio = od / "tts_finish_the_course.mp3"
    files = parallel_render_scenes(__file__, scene_count=6, topic="finish_the_course", audio_path=str(audio))
    final = od / "finish_the_course_final.mp4"
    concat_scenes(files, str(audio), str(final), validate_audio=str(audio))

    mb = final.stat().st_size / 1024 / 1024
    print(f"\n{'='*60}\n  RENDER COMPLETE: {final}\n  {mb:.1f} MB | {time.time()-t0:.1f}s\n{'='*60}")
    try:
        from render_utils import run_post_render_qa
        run_post_render_qa(str(final), scene_count=6)
    except ImportError: pass
