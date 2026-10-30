# Director's audio and timing cues — Adam cut

**Master:** selected Adam US voice, unaltered speech timing, 56.388 seconds; film duration 58.4 seconds at 30 fps (1,752 frames). Each scene starts at its measured voice segment start. The eight original storyboard ranges were provisional; these replace them. Cue-to-speech timing is scene-level; typography phrase timing is estimated from each measured segment, not forced aligned. Verify exact wording by listening before claiming word-level synchronization.

**Mix approach:** original synthesized instrumental bed throughout, understated below narration, no background silence; separate original synthesized SFX, transient level restrained so consonants remain clear. 0.22-second scene gaps are intentional breaths. Bed fades at the end, leaving narration uncut. Times below are seconds from start; frames are zero-based.

| Scene / absolute frames | Voice & visual | Music / SFX cues |
|---|---|---|
| 1 · 0–195 · 0.000–6.556s | Why the dollar? Coin and connected paths. Camera pulls back; types build and travel. | Low pulse begins at 0.00; fine sweep at 0.30; metallic dollar accent at 1.25; connection clicks at 3.0 and 4.6. Wipe swell at 6.32. |
| 2 · 196–496 · 6.556–16.568s | Bretton Woods, 1944. Currency nodes, the dollar, gold bar and official convertibility; camera arcs around the objects. | Music opens with higher pad at 6.56. Gold settlement hit at 6.75; clicks at 8.40, 9.25 and 10.05; gold link tone at 13.40; fracture sweep at 16.30. |
| 3 · 497–699 · 16.568–23.337s | 1971; the gold link separates. Dollar remains, network persists. | Thin crack at 16.80; restrained impact at 17.35; low release at 19.6; return of pulse at 20.85; sweep at 23.08. |
| 4 · 700–925 · 23.337–30.875s | Economy, Treasury securities, deep markets and trading motion. | Music becomes more rhythmic at 23.34. Air-paper whoosh 24.15; document clicks 25.30, 26.15 and 26.90; trade ticks 28.2 and 28.7; swipe at 30.60. |
| 5 · 926–1118 · 30.875–37.281s | Trade, banks and reserve nodes connect to the dollar. | Three focused cues: container accent 31.25, loan click 33.55, vault hit 35.55. Connection sweep 37.00. |
| 6 · 1119–1298 · 37.281–43.283s | Network loop; nodes activate and make subsequent connections. | Three-note sequence at 38.20, 38.75 and 39.30; circulating high ticks at 40.10 and 41.10; release 43.05. |
| 7 · 1299–1478 · 43.283–49.305s | Other currencies compete; confidence can change. | Pull bed back slightly; entry notes 43.65, 44.15, 44.65; muted low tension accent 46.80; return sweep 49.05. |
| 8 · 1479–1751 · 49.305–58.400s | Dollar leads, not alone: history, markets and habit. End on moving network. | Warm resolution chord at 49.65. Single accents at 52.2, 53.4 and 54.45; musical tail starts fading at 56.5; silence only at final fade, after speech. |

**Editorial deviations to track:** Camera motion, geometry, words, and SFX must be compared with `MOTION_SCRIPT.md` shot by shot. Any unrealized direction, inaccessible alignment or quality gate is recorded in `AUDIT.md`; no claim of complete conformance without evidence. No Blender or third-party photos. Music and effects generated procedurally in `scripts/sound.py`.

## Implementation clarification
The 42 event times are implemented as synthetic sounds listed in `assets/sound-cues.json`. Their descriptive labels above indicate the intended dramatic function: paper, fracture, vault and container cues are abstract sweeps/ticks/impacts, not literal foley. The continuous music is a repeating synthesized chord and pulse with a global fade, not a section-specific pad expansion, tension duck, or separately triggered resolution chord. See `AUDIT.md` for other deviations.
