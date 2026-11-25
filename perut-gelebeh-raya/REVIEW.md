# Trim Gelebeh Perut untuk Raya 2027? — review notes

Follows `../FORMAT.md` (no voiceover): 1080×1920, 60 fps, 60.5 s, 8 clips, headline 100 / sub 47 / caption 40 /
label 19 px, footage sound −57 LUFS per clip, HDR iPhone clips tone-mapped to SDR, synthesised SFX, ~70 MB delivery
(`renders/Perut-Gelebeh-Raya-FINAL-70MB.mp4`).

## Brief → film

| Brief | Where |
|---|---|
| Hook "Trim gelebeh perut untuk raya 2027? Buat 3 senaman ni" | c01, one continuous shot (halo round the head, `114808`, not used as an intro before) |
| CTA kecil "Save & repost video sebelum hilang" | Sticker under the hook, bookmark + spinning repost icon |
| Russian twist / Kettlebell halos / Lateral knee tuck, 12 s each | c02 / c03 / c04 (IMG_2774 / IMG_2772 / IMG_2779 — lateral knee tuck is IMG_2779 per the client's earlier correction) |
| 12 reps × 3 set, rehat 1 minit | "SETIAP LATIHAN / 12 REPS × 3 SET" bottom-left with a live countdown on each rep seen; 1:00 → 0:00 rest timer bottom-right |
| Otot yang bekerja | "Otot bekerja" card for the whole clip: obliques (Gray's 392), core & bahu (397), perut depan & sisi (397 + 392) |
| Afterburn effect | c05: EPOC diagram (Wikimedia Commons, CC BY-SA 4.0, credit on screen) with "masa workout" / "lepas workout" highlights, then "AFTERBURN EFFECT" and the caption "Kalori terus terbakar lepas workout" |
| USP lembut, tak pecah, tak sakit | c06 squeeze, c07 drop test (shake + impact on both hits, 51.20 / 54.65 s) |
| CTA | c08 "NAK KECILKAN PERUT?" + "Start berlatih SEKARANG!" + "Kettlebell kat beg kuning" + arrows far left |

The brief's final CTA said "Nak kecilkan **peha**?" while the whole video is about the belly; the film says **PERUT** —
one word to change in `tools/build.py` (g08) if peha was meant.

## Rep timing
Twist = kettlebell at each side, halo = kettlebell at the top of the circle, knee tuck = knees at each side
(`tools/track_color.py` pink / shoe + 5 fps strips). Countdown from 12: twist 9.00 … 16.55 (8 reps), halos 21.00 / 23.30 /
25.50 / 27.80, knee tuck 32.80 … 39.90 (8 reps). Reps while the block is still arriving are not counted.

## Checks
- `hyperframes check`: 0 errors. Warnings kept: the halos muscle card edge near YouTube's right overlay; two contrast
  warnings on yellow/pink words with a thick black stroke; craft text-size notes on the 19 px format labels.
- Snapshots of every scene and the end frame.
