# Video Analysis Brief

## Source

- Input: `video/dollar-world-currency.mp4`
- Source kind: `local-file`
- Duration: `66.366667` seconds
- Resolution: `1920x1080`
- Video codec: `h264`
- Audio present: `True`

## Evidence Artifacts

- `ffprobe_json`: `/home/user/AGENT_RULES/video/audit/final-evidence/dollar-world-currency-20261029-160714/ffprobe.json`
- `quality_gates`: `/home/user/AGENT_RULES/video/audit/final-evidence/dollar-world-currency-20261029-160714/quality-gates.json`
- `frames`: `['/home/user/AGENT_RULES/video/audit/final-evidence/dollar-world-currency-20261029-160714/frames/frame-01-00-00-03_904.jpg', '/home/user/AGENT_RULES/video/audit/final-evidence/dollar-world-currency-20261029-160714/frames/frame-02-00-00-07_808.jpg', '/home/user/AGENT_RULES/video/audit/final-evidence/dollar-world-currency-20261029-160714/frames/frame-03-00-00-11_712.jpg', '/home/user/AGENT_RULES/video/audit/final-evidence/dollar-world-currency-20261029-160714/frames/frame-04-00-00-15_616.jpg', '/home/user/AGENT_RULES/video/audit/final-evidence/dollar-world-currency-20261029-160714/frames/frame-05-00-00-19_520.jpg', '/home/user/AGENT_RULES/video/audit/final-evidence/dollar-world-currency-20261029-160714/frames/frame-06-00-00-23_424.jpg', '/home/user/AGENT_RULES/video/audit/final-evidence/dollar-world-currency-20261029-160714/frames/frame-07-00-00-27_327.jpg', '/home/user/AGENT_RULES/video/audit/final-evidence/dollar-world-currency-20261029-160714/frames/frame-08-00-00-31_231.jpg', '/home/user/AGENT_RULES/video/audit/final-evidence/dollar-world-currency-20261029-160714/frames/frame-09-00-00-35_135.jpg', '/home/user/AGENT_RULES/video/audit/final-evidence/dollar-world-currency-20261029-160714/frames/frame-10-00-00-39_039.jpg', '/home/user/AGENT_RULES/video/audit/final-evidence/dollar-world-currency-20261029-160714/frames/frame-11-00-00-42_943.jpg', '/home/user/AGENT_RULES/video/audit/final-evidence/dollar-world-currency-20261029-160714/frames/frame-12-00-00-46_847.jpg', '/home/user/AGENT_RULES/video/audit/final-evidence/dollar-world-currency-20261029-160714/frames/frame-13-00-00-50_751.jpg', '/home/user/AGENT_RULES/video/audit/final-evidence/dollar-world-currency-20261029-160714/frames/frame-14-00-00-54_655.jpg', '/home/user/AGENT_RULES/video/audit/final-evidence/dollar-world-currency-20261029-160714/frames/frame-15-00-00-58_559.jpg', '/home/user/AGENT_RULES/video/audit/final-evidence/dollar-world-currency-20261029-160714/frames/frame-16-00-01-02_463.jpg']`
- `contact_sheet`: `/home/user/AGENT_RULES/video/audit/final-evidence/dollar-world-currency-20261029-160714/contact-sheet.jpg`

## Evidence Rules

- Metadata supports file, stream, duration, and codec claims.
- Sampled frames and the contact sheet support visible-scene claims only for sampled timestamps.
- OCR is weaker than subtitles or ASR and may contain recognition errors.
- Spoken wording requires subtitle or ASR evidence.
- If a claim is not supported by an artifact, label it as unsupported.

## Initial Conclusion

A reusable artifact set exists. Review `contact-sheet.jpg`, `frames/`, subtitles or ASR outputs, and `quality-gates.json` before making content claims.
