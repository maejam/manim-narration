# Manim Narration

Manim Narration is a [Manim](https://manim.community) plugin to add narrations to your scenes.
It is heavily inspired by and is a complete rewrite of [manim-voiceover](https://github.com/ManimCommunity/manim-voiceover)


## What is similar to manim-voiceover?

The public api is pretty much the same (see the example below).

All the very good ideas from the original library are still there...
- Add narrations through a context manager (`with self.narration(...):`).
- Easily set and change the speech service.
- Use bookmarks to trigger animations at specific words in the narration.

...or are planned to be added in future realeases:
- recording service
- translation


## What is different, then?

- Up-to-date dependencies.
- Largely tested (python3.10->3.13) to ensure code quality.
- Configurable programmatically or through environment variables, a dotenv file, pyproject.toml or toml config files.
- Extensible: add new speech services, alignment services or tags (relatively) easily.
- Possible to set more than one speech service: a scene with several characters, speaking different languages or with different voices for example.
- Choose the service to use to align text and speech (bookmarks) depending on your use case: manually / fast and not very accurate / slow and very accurate.

### Available speech services

| Service   | type    | Languages              | Inference time (cpu)   | Audio sample                                               |
|-----------|---------|------------------------|------------------------|------------------------------------------------------------|
| Coqui*    | Offline | 1100+                  | 11.06 seconds          | [sample](benchmarks/narrations/CoquiService.wav?raw=True)  |
| GTTS      | Online  | en/fr/zh/pt/es         | 0.76 seconds           | [sample](benchmarks/narrations/GTTSService.wav?raw=True)   |
| Kokoro    | Offline | en/jp/zh/es/fr/hi/it/pt| 2.15 seconds           | [sample](benchmarks/narrations/KokoroService.wav?raw=True) |

<sub>*Coqui provides 70+ tts models. The one being benchmarked here is "xtts_v2"</sub>

### Available alignment services

| Service       | Description                                          | type    | Inference time (cpu)   | Distance from truth |
|---------------|------------------------------------------------------|---------|------------------------|---------------------|
| Manual        | Lets the user manually align text and speech.        | Offline | 0.0 seconds            |          irrelevant |
| Interpolation | timestamp = audio_duration * char_offset / len(text) | Offline | 0.0 seconds            |                3.24 |
| CTC*          | Let a CTC model from HuggingFace do the alignment    | Offline | 13.02 seconds          |                0.18 |

<sub>*pretrained Wav2Vec2, HuBERT, and MMS models from HuggingFace can be used. The one being benchmarked here is the default model (https://huggingface.co/MahmoudAshraf/mms-300m-1130-forced-aligner)</sub>


## More to come

- More speech and alignment services.
- Generate music and not just speech.
- Align subcaptions precisely with Alignment services.
- A proper PyPi package.
For now install by cloning the repo. Example using uv:
```
git clone https://github.com/maejam/manim-narration.git
cd manim_narration
uv pip install -e .
# uv pip install -e .[coqui] to install with extra `coqui` (see `pyproject.py` for more extras)
```
or adding as a dependency to your project:
```
uv init myproject
cd myproject
uv add git+https://github.com/maejam/manim-narration.git
# uv add git+https://github.com/maejam/manim-narration.git[coqui] to install with extra `coqui` (see `pyproject.py` for more extras)
```
- A proper documentation. For now, see the in-code documentation.
- Other ideas you might implement. Contributions are welcomed.


## Example

Just like voiceover, render scenes with `--disable_caching` to avoid bugs



https://github.com/user-attachments/assets/0659769a-8210-453b-9d61-8f664e63211e



```python
import manim as m

from manim_narration import NarrationScene
from manim_narration.alignment import InterpolationAligner
from manim_narration.speech import GTTSService


class GettingStarted(NarrationScene):
    def construct(self):
        # define speech services with a name
        self.set_speech_services(en=GTTSService(lang="en"), fr=GTTSService(lang="fr"))
        # optionally set an alignment service (ManualAlignment is the default)
        self.set_alignment_service(InterpolationAligner())

        en = m.Text(
            "Narration is the use of a written or spoken\n commentary to convey a "
            "story to an audience.",
            font_size=30,
        )
        comm = m.Text("commentaire", font_size=30).next_to(en, m.DOWN)
        hist = m.Text("histoire", font_size=30).next_to(comm, m.RIGHT)

        # the first argument is the speech service to use.
        # if it is not set, the first one will be used.
        with self.narration(text=en.text) as narration:
            self.play(m.Write(en), run_time=narration.duration)
        with self.narration(
            "fr",
            text="Une narration consiste a utiliser un <bookmark mark='comm'/>"
            "commentaire écrit ou parlé afin de transmettre une "
            "<bookmark mark='hist'/>histoire à un public.",
        ) as narration:
            # adjust the timing with `offset` and adding to `run_time` if needed
            self.wait_until_bookmark("comm", offset=-0.5)
            self.play(
                m.Write(comm), run_time=narration.duration_until_bookmark("hist") - 0.5
            )
            self.play(m.Write(hist), run_time=narration.remaining_duration)
```
