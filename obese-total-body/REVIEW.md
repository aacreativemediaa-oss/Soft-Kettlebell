# Obese Tapi Malas Nak Jogging? — review notes

Follows `../FORMAT.md` (no voiceover): 1080×1920, 60 fps, 65.5 s, 9 clips, headline 100 / sub 47 / caption 40 /
label 19 px, footage sound −57 LUFS per clip (c06 muted: its soundtrack classifies as music, AudioSet AST ~0.5),
synthesised SFX, ~70 MB delivery (`renders/Obese-Total-Body-FINAL-70MB.mp4`).

## Brief → film
| Brief | Where |
|---|---|
| Hook "Obese tapi malas nak jogging? Buat 3 senaman mudah ni" | c01, one continuous shot at the running track (not used as an intro before) |
| CTA kecil "Save & repost video sebelum hilang" | Sticker under the hook |
| Goblet squat / Kettlebell halos / Kettlebell swing, 12 s each | c02 / c03 / c04 |
| 12 reps × 3 set, rehat 1 minit | "SETIAP LATIHAN / 12 REPS × 3 SET" with a live countdown on each rep seen; 1:00 → 0:00 rest timer |
| Otot yang bekerja | Gray's Anatomy cards: 430 + 434 (peha & punggung), 397 (bahu & core), 434 (punggung & hamstring) |
| Total body workout | c05: "Kombinasi 3 senaman ni = TOTAL BODY WORKOUT" with what each move trains |
| Afterburn effect | c06: EPOC diagram (Wikimedia Commons, CC BY-SA 4.0, credit on screen), workout / after-workout highlights, "Kalori terus terbakar lepas workout" |
| USP lembut, tak pecah, tak sakit | c07 squeeze, c08 drop test (shake + impact at 56.20 / 59.65 s) |
| CTA "2027 nak upgrade body? Start bersenam sekarang" | c09 headline + button, "Kettlebell kat beg kuning", arrows far left |

## Rep timing (`tools/rep_times.py`)
Goblet = bottom of the squat 9.70 / 11.50 / 13.15 / 14.95; halos = kettlebell over the head 21.60 / 23.50 / 25.80 / 27.90;
swing = kettlebell at chest height 33.45 / 34.90 / 36.50 / 38.15 / 39.75 s.

## Checks
- `hyperframes check`: 0 errors. Warnings kept: two muscle-card edges a few px into the YouTube/TikTok right overlay;
  one contrast warning on a pink word with a thick black stroke.
- Snapshots of every scene and the end frame.
