# 3 Kelebihan (rakaman VO ke-2) — review notes

1080×1920, 60 fps, 70.48 s, HyperFrames 0.9.65. Same format and look as `../video` (first edit of this script),
re-timed to the new voiceover, with the client's later updates built in: "link beg kuning", CTA arrows on the far
left, fact images (EPOC diagram for afterburn, PubChem testosterone structure), delivery file under 45 MB.

## Cuts (10, cut inside VO pauses)

| # | Film time | Source (trim) | VO |
|---|---|---|---|
| c01 | 0.00–7.45 | IMG_2536b.mov (0.0) — **intro, one shot, normal speed; not used as an intro before** | Hook + save & repost |
| c02 | 7.45–15.12 | video_20260621_114944.mp4 (0.0) | #1 Bakar kalori, kardio |
| c03 | 15.12–22.55 | video_20260621_114605.mp4 (10.0) | Latihan beban, afterburn (EPOC diagram) |
| c04 | 22.55–33.15 | video_20260316_010826.mp4 (1.0) | #2 Posture, core/bahu/back |
| c05 | 33.15–39.15 | IMG_1994.mov (0.3) | Lenguh → tegap & melentik |
| c06 | 39.15–45.25 | IMG_1992.mov (0.0) | #3 Gelebeh |
| c07 | 45.25–51.28 | video_20251226_112938.mp4 (0.5) | Peha, perut, lengan |
| c08 | 51.28–59.55 | video_20260713_134440.mp4 (2.0) — kettlebell swing (client asked for a different shot than the red-shirt clip) | Bukan sado, testosteron (molecule card) |
| c09 | 59.55–66.08 | IMG_1028.mov (0.0) | Konsisten, hasil |
| c10 | 66.08–70.48 | video_20260523_100816.MP4 (18.0) | CTA link beg kuning |

All chosen segments: no music (AudioSet AST) → footage sound at 30 %. VO copied bit-for-bit, volume 1.

## Words corrected from Whisper (please confirm)

"pre-swab" → **brisk walk**, "akan gelembik" → **kurangkan gelebeh**, "link back kuning" → **link beg kuning**,
"sadur" → **sado**, "lengoh" → **lenguh**, "bagian" → **bahagian**. The first two sit in clauses shown by graphics, so
they never appear as captions.

## Checks

- `hyperframes check`: 0 errors; one contrast warning kept (pink "3" in the hook, thick black stroke).
- Snapshots of every scene and the end frame (button "LINK BEG KUNING", "Harga tengah MURAH!", arrows far left).
- VO sync measured on the delivery file with `tools/verify_vo_sync.py`.
