# 3 Senaman untuk Gelebeh Peha — review notes

1080×1920, 60 fps, 49.0 s, HyperFrames 0.9.65. Same format as `../video` (first Soft Kettlebell edit), with its later
client updates: fact images from search, CTA arrows on the far left, "beg kuning" wording, and a ≤ 45 MB delivery file.

## Brief → film

| Brief | Where |
|---|---|
| Hook: 3 senaman untuk gelebeh peha | c01, one continuous shot at normal speed — a **different** intro shot from the first video (thigh close-up `video_20251226_112938`, not `IMG_1026`) |
| 1. Goblet Squat + tip "partial squat" | c02 demo + front-thigh anatomy; c03 tip card + depth gauge on a half-depth box squat |
| 2. Forward Lunges + tip | c04 demo; c05 tip "Lutut 90° — lutut depan jangan lepas hujung kaki" + lunge diagram |
| 3. Sumo Squat + tip | c06 demo + inner-thigh anatomy; c07 tip "Hujung kaki pusing 45° keluar, lutut ikut arah jari kaki" + feet diagram |
| USP: lembut, tak pecah, tak sakit kaki | c08 squeeze ("Material lembut"), c09 drop test on a bare foot (checks land on the two drops, camera shake + impact) |
| CTA | c10: "Nak trim gelebeh peha?" + "Grab kettlebell kat beg kuning sekarang!" |

Tips for #2 and #3 were written by me (the brief gave only the #1 example): standard coaching cues — please confirm.

## Format checklist

- 10 clips, zoom-in 1.00 → 1.08 on each, white flash on all 9 cuts; no speed changes.
- No voiceover, no music. Footage sound at 30 %; c04 is muted because its ambience classifies partly as music (AudioSet AST up to 0.29).
- Anton titles/captions, Montserrat labels (70 % scale: 140/112/84/36 px). Captions 60 px uppercase, black stroke,
  2–3 words, active word yellow, keywords neon green, centre-bottom; no caption repeats a line a graphic already shows.
- SFX synthesised (`tools/sfx.py`): whoosh ×3 takes, pop ×2, ding (one per tip), impact, riser → impact on the drop, zap, cha-ching. Low level.
- All graphics inside the TikTok/Reels/Shorts safe area; CTA arrows far left above the yellow-basket link.

## Fact images

| Image | Use | Source / licence |
|---|---|---|
| `gray430-thigh-front.png` | Goblet squat — "Sasar: peha depan" | Gray's Anatomy (1918) plate 430, Wikimedia Commons — public domain |
| `gray433-thigh-inner.png` | Sumo squat — "Sasar: peha dalam" (adductors) | Gray's Anatomy (1918) plate 433, Wikimedia Commons — public domain |

## Checks

- `hyperframes check`: 0 errors. Two contrast warnings kept: pink/yellow display words with a thick black stroke.
- Snapshots of every scene; headers moved above the subject's face in #1/#2/#3.
- Render verified with ffprobe (60 fps, frame count) and a frame from the end card.
