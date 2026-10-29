# Evidence Grading

Use this hierarchy when answering from a video-analysis run.

## Evidence Classes

- `source-metadata`
  Claims supported by source metadata, ffprobe stream data, duration, codec, and file information.

- `subtitle-or-transcript`
  Claims supported by harvested subtitles or an ASR transcript. Use this class for speech-dependent conclusions.

- `sampled-frames`
  Claims supported by extracted frames, contact sheets, visible scene content, and timestamped frame evidence.

- `ocr`
  Claims supported by OCR from sampled frames. OCR is weaker than subtitles or ASR and may misread text.

- `surrounding-context`
  Claims supported only by the page, title, post text, or surrounding description. This is not proof of video contents.

- `unsupported`
  Claims not supported by any artifact.

## Rules

- Do not claim spoken wording from frames alone.
- Do not claim exact chronology between sampled frames unless timestamps or transcript support it.
- Do not claim what happens after the sampled frames unless an artifact shows it.
- Treat OCR as approximate unless the text is clear in the frame.
- If no transcript exists, avoid strong claims about exact speech.
- If a result depends on a missing artifact, state the gap.
