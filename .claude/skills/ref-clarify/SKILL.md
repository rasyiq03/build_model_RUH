---
name: ref-clarify
description: >
  Opens a reference IMAGE in the user's browser so they can annotate it (drop
  numbered pins with comments, draw boxes/arrows, write an answer) AND/OR upload
  additional reference files (a clearer photo, a floor plan) as their answer,
  then reads the result back as clearer context. ALWAYS use this — instead of
  guessing —
  whenever a reference image is ambiguous, low-detail, or you cannot identify an
  element; whenever TWO OR MORE references disagree (different shape, count,
  layout, or era); or whenever you are about to assume something about a build
  shape that the references do not clearly show. Trigger on phrases/situations
  like "which part is…", "I can't tell from the image", "the references
  conflict", "is this the green Mas'a zone or a walkway", or any time the RUH
  Reference Folder Protocol says to escalate a visual question to the user. Do
  not invent an answer when this skill could get a real one from the user.
---

# ref-clarify — ask the user about a reference image (don't guess)

When a reference image is unclear or two references conflict, **do not guess and
do not silently pick one.** Run this tool: it shows the user the exact image with
your question, lets them mark it up and comment, and hands you back an annotated
image plus structured notes. Then continue the build from the user's answer.

This is the concrete mechanism for the "contradiction / ambiguity → ask the
user" rule in the RUH master `AGENTS.md` and each model's Reference Folder
Protocol.

## When to use (be eager, not shy)

- You cannot identify an element, its shape, scale, count, or material from the image.
- Two or more references disagree (form, layout, level count, era/expansion phase).
- The image is low-resolution, partially obscured, or could be read two ways.
- You are about to *assume* a build dimension/shape the references don't clearly show.

If you find yourself writing "I'll assume…" about something visual, stop and use
this skill instead.

## How to run

The script is pure Python standard library — no install needed. From the model's
folder (so outputs land next to its references):

```bash
python .claude/skills/ref-clarify/scripts/ref_annotate.py \
    "<path/to/reference_image>" \
    --question "<the specific thing you need clarified>"
```

Options:
- `--out-dir DIR` — where to write outputs (default: `<image_dir>/_clarify`).
  For RUH, prefer the model's own folder, e.g. `--out-dir models/<model>/references/_clarify`.
- `--port N` — fixed port (default: auto).
- `--no-browser` — don't auto-open a browser (testing only).

The command **blocks** until the user clicks "Save & Finish" in their browser —
that is intended (human-in-the-loop). Keep your question narrow and specific;
ask about one ambiguity at a time.

## How to read the result

When the command returns, parse its stdout for two paths:

```
[ref-clarify] annotated_image: <...>__annotated.png
[ref-clarify] notes_json:      <...>__notes.json
```

1. **View the annotated PNG** — you can see it. The user's pins, boxes, and
   arrows show exactly what they mean on the image.
2. **Read the notes JSON**, which has:
   - `answer` — the user's overall reply to your question (treat as ground truth);
   - `pins` — `[{n, x, y, comment}]`, each numbered marker with its note;
   - `shapes` — boxes/arrows/freehand in image-pixel coordinates;
   - `uploaded_references` — absolute paths to any NEW reference files the user
     uploaded as their answer (e.g. a clearer photo or floor plan). View these
     too — they are authoritative. Consider copying them into the right
     `references/<type>/` subfolder so the new reference is kept with the model.
   - `source_image`, `image_size`, `timestamp`.

Use the user's answer + pins as authoritative over your own reading of the raw
image. If it's still unclear, run the tool again with a sharper question.

If stdout prints `[ref-clarify] CANCELLED` instead, the user closed the tool
without adding anything (no files are written). In that case, ask the question in
plain text, or proceed with your best assumption — clearly flagged to the user.

## After clarifying

Record the resolution so it isn't re-litigated: add a short line to the model's
`AGENTS.md` (e.g. under `## C. Calibration & Trace` or the USER OVERRIDE block),
referencing the `__notes.json`. This keeps the decision traceable and stops the
same contradiction from recurring.

## Environment note

Needs a desktop where a browser can open for the user (the user's local machine
with Blender qualifies). On a headless/remote host the browser won't appear to
the user — in that case, fall back to asking the question in plain text.
