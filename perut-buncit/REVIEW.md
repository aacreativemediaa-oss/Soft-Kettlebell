# 3 Senaman untuk Perut Buncit — review notes

Same style and format as `../lemak-peha` (no voiceover): 1080×1920, 60 fps, 49.0 s, 10 cuts, zoom-in + white flash on
every cut, no music, footage sound 30 % (no chosen clip has music), Anton/Montserrat at 70 % scale, captions 60 px,
synthesised SFX, CTA arrows on the far left, delivery file under 45 MB.

## Changes from the brief

- Hook "3 senaman untuk perut buncit", mini hook "Save & repost video". Intro shot `IMG_2777` (new footage; not used as an intro before).
- Education: 1. Russian Twist, 2. Kneeling Halos, 3. Side to Side Leg Raise — demos on the new purple-shirt footage
  (IMG_2774, IMG_2772, IMG_2779). One core tip each (written by me — please confirm):
  1. "Belakang lurus, putar bahu — bukan tangan je" (+ top-view rotation diagram)
  2. "Badan jangan goyang, perut ketat, kettlebell rapat kepala" (+ halo path diagram)
  3. "Baru mula? Lutut bengkok — kaki lurus bila dah kuat" (+ bent → straight legs diagram)
- CTA headline changed to "Nak kecilkan perut buncit?" to match the topic (button unchanged: "Grab kettlebell kat beg kuning sekarang!").

## Client corrections

- Hook tag "Kettlebell di rumah" removed.
- Tip #3 footage: `IMG_2775` is a **Lateral Knee Tuck**, not the side to side leg raise; replaced with a later segment of
  `IMG_2779` (9.5 s), where the legs pass over the kettlebell. `IMG_2775` is no longer used.

## Fact images

| Image | Use | Source / licence |
|---|---|---|
| `gray392-oblique.png` | Russian twist — "Sasar: perut sisi" | Gray's Anatomy (1918) plate 392, Wikimedia Commons — public domain |
| `gray397-rectus.png` | Leg raise — "Sasar: perut depan" | Gray's Anatomy (1918) plate 397, Wikimedia Commons — public domain |

## Colour

The new iPhone clips (IMG_27xx) are HDR (HLG, BT.2020). They are tone-mapped to SDR BT.709 in `tools/prep_footage.sh`
(zscale + hable) and the film renders with `--sdr`; without this HyperFrames promoted the whole render to HDR and the
graphics and footage looked washed out after conversion.

## Checks

- `hyperframes check`: 0 errors; one contrast warning kept (pink display word with thick black stroke).
- Snapshots of every scene; #3 anatomy card and the halo diagram moved off the model's face.
