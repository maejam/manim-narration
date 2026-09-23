## v1.2.0 (2026-09-23)

### Feat

- **benchmarks**: add `generate_samples` script
- **benchmarks**: add concurrency to speech services benchmark
- **narrations**: add option to ignore cache when generating a narration
- **narrations**: add concurrency for speech generation

### Fix

- **tracker**: add __str__ to NarrationTracker
- **bookmarks**: improve error message when a bookmark is not found
- **concurrency**: improve multiprocessing stability
- **chatterbox**: fix parameters to multilingual model

### Refactor

- **tracker**: simplify instantiation
- **narrations**: decouple narration generation and playback
- **narrations**: move skipping narrations checks into properties

## v1.1.0 (2025-11-05)

### Feat

- **narrations**: add option to skip narrations per-section
- **narrations**: add option to skip narrations globally
- **speech**: add Chatterbox service
