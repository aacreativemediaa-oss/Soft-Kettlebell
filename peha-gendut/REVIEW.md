# Peha Gendut? Buat 3 Latihan Ni — review notes

Follows `../FORMAT.md` (no voiceover): 1080×1920, 60 fps, 51.8 s, 8 clips, headline 100 / sub 47 / caption 40 /
label 19 px, footage sound −57 LUFS per clip (`tools/level_footage.py`), HDR sources tone-mapped to SDR, synthesised
SFX, ~70 MB delivery (`renders/Peha-Gendut-FINAL-70MB.mp4`, 2-pass 10.6 Mbps).

## Brief → film

| Brief | Where |
|---|---|
| Hook "Peha Gendut? Buat 3 Latihan ni" | c01, one continuous thigh close-up at normal speed |
| CTA kecil "Save & repost video sebelum hilang" | Sticker under the hook with bookmark + repost icons |
| 1. Kettlebell swing / 2. Goblet squat / 3. Forward lunges, 10 s each | c02 / c03 / c04, one 10 s clip per exercise |
| 12 reps × 3 set, rehat 1 minit | "SETIAP LATIHAN / 12 REPS × 3 SET" bottom-left (one line, same width) with a live rep countdown that drops on each rep seen in the footage; 1:00 → 0:00 rest timer bottom-right, counting over the clip |
| Tunjuk otot yang bekerja | "Otot bekerja:" card for the whole clip — swing: punggung & hamstring (Gray's 434); goblet: peha depan / quadriceps (Gray's 430); lunges: peha & punggung (430 + 434) |
| USP lembut, tak pecah, tak sakit | c05 squeeze, c06 drop test on a bare foot (shake + impact on both hits, 37.90 / 41.35 s) |
| USP 4kg hingga 12kg | c07 "4KG HINGGA 12KG": real photo cards for 4 / 6 / 8 KG; 10 KG and 12 KG are drawn icons because the Drive folder has no footage of those weights |
| CTA "Nak kecilkan peha? Start berlatih sekarang" | c08 headline + button, "Kettlebell kat beg kuning" pill with arrows on the far left |

## Rep timing

Reps were found from the footage (`tools/rep_times.py` head height / `tools/track_color.py`); reps during the block's
arrival are not counted. Countdown starts at 12: swing 8.45 / 9.95 / 11.60 / 13.20, goblet 18.95 / 20.60 / 22.40,
lunges 29.30 / 31.50 / 33.40 s — each with a pop SFX and a yellow punch on the number.

## Checks

- `hyperframes check`: 0 errors. One warning kept: the swing muscle card edge sits a few px inside TikTok's right-edge
  overlay zone (x > 888 at t 8.6) — clear of the like/comment column.
- Snapshots of every scene; frame strip from the final file at 2.8 / 8.6 / 13.0 / 19.0 / 29.4 / 35.5 / 40.7 / 44.6 / 51.75 s.
- Render verified with ffprobe (SDR bt709, 60 fps, 3108 frames).
