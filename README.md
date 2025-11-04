# Manim Narration

Manim Narration is a [Manim](https://manim.community) plugin to add narrations to your scenes.
It is heavily inspired by and is a complete rewrite of [manim-voiceover](https://github.com/ManimCommunity/manim-voiceover)


## What is similar to manim-voiceover?

The public API is pretty much the same (see the example below).

Most of the very good ideas from the original library are still there:
- Add narrations through a context manager (`with self.narration(...):`).
- Easily set and change the speech service.
- Use bookmarks to trigger animations at specific words in the narration.


## What is different, then?

- Up-to-date dependencies.
- Largely tested (python3.10->3.13) to ensure code quality.
- Configurable programmatically or through environment variables, a dotenv file, pyproject.toml or toml config files.
- Extensible: add new speech services, alignment services or tags (relatively) easily.
- Possible to set more than one speech service: a scene with several characters, speaking different languages or with different voices for example.
- Choose the service(s) to use to align text and speech (bookmarks and subcaptions) depending on your use case: manually / fast and not very accurate / slow and very accurate.

Missing features:
- recording service
- translation


### Available speech services

Check the `benchmarks/` directory to see how the statistics below are produced. You can also run the benchmark scripts on your setup.

| Service    | type    | Languages              | Inference time (cpu) | Audio sample                                               |
|------------|---------|------------------------|----------------------|------------------------------------------------------------|
| Coqui*     | Offline | 1100+                  | 11.06 seconds        | [sample](benchmarks/narrations/Coqui.wav?raw=True)         |
| GTTS       | Online  | en/fr/zh/pt/es         | 0.76 seconds         | [sample](benchmarks/narrations/GTTS.wav?raw=True)          |
| Kokoro     | Offline | en/jp/zh/es/fr/hi/it/pt| 2.15 seconds         | [sample](benchmarks/narrations/Kokoro.wav?raw=True)        |
| Chatterbox | Offline | 23 languages           | 39.19 seconds        | [sample](benchmarks/narrations/Chatterbox.wav?raw=True)    |

<sub>*Coqui provides 70+ tts models. The one being benchmarked here is "xtts_v2"</sub>

### Available alignment services

The role of the `aligners` is to match up the text spoken in the generated audio file with the time when it is spoken. They are only useful when using bookmarks or for synchronizing subcaptions.

| Service       | Description                                          | type    | Inference time (cpu)   | Distance from truth |
|---------------|------------------------------------------------------|---------|------------------------|---------------------|
| Manual        | Lets the user manually align text and speech         | Offline | 0.0 seconds            |          irrelevant |
| Interpolation | timestamp = audio_duration * char_offset / len(text) | Offline | 0.0 seconds            |                3.24 |
| CTC*          | Let a CTC model from HuggingFace do the alignment    | Offline | 13.02 seconds          |                0.18 |

<sub>*pretrained Wav2Vec2, HuBERT, and MMS models from HuggingFace can be used. The one being benchmarked here is the default model (https://huggingface.co/MahmoudAshraf/mms-300m-1130-forced-aligner)</sub>

> [!NOTE]
> Running local services such as `Coqui`, `Kokoro` and `CTCAligner` for the first time will trigger the download of the models. This can be a lengthy process but the models are then cached.


## Installation

For now there is no Pypi package. Install by adding to your `manim` project:
- create the project if necessary:
```
uv init myproject
cd myproject
```
- add the plugin to your newly created or existing project with all the available services:
```
uv add git+https://github.com/maejam/manim-narration.git[full]
```


## Documentation
For now there is no dedicated documentation. See the in-code documentation.


## Example

> [!IMPORTANT]
> Just like voiceover, render scenes with `--disable_caching` to avoid bugs

> [!NOTE]
> The example below uses `CTCAligner` and `GTTSService`.
> To run it you must install with `gtts` and `ctc` extra (or use another aligner).

<sub>Activate the sound under the video.</sub>

https://github.com/user-attachments/assets/c582194b-2c0d-4449-97f8-d7ee4320f248


```python
import manim as m

from manim_narration import NarrationScene
from manim_narration.alignment import CTCAligner, InterpolationAligner
from manim_narration.speech import GTTSService


class GettingStarted(NarrationScene):
    def construct(self) -> None:
        # define speech services with a name
        self.set_speech_services(
            en=GTTSService(lang="en"),
            fr=GTTSService(lang="fr"),
        )
        # optionally set alignment services
        # would default to: {"default": InterpolationAligner()}
        self.set_alignment_services(
            bookmarks=InterpolationAligner(),
            subcaptions=CTCAligner(language="fr"),
        )

        en_txt = (
            "Narration is the use of a written or spoken \n"
            "commentary to convey a story to an audience."
        )

        en = m.Text(en_txt, font_size=30)
        comm = m.Text("commentaire", font_size=30).next_to(en, m.DOWN)
        hist = m.Text("histoire", font_size=30).next_to(comm, m.RIGHT)

        # the first argument to the context manager is the speech service to use.
        # (defaults to the first in set_speech_services)
        # the second argument is the aligner to use for bookmarks
        # (defaults to the first in set_alignment_services)
        # Using default services is very concise, just like voiceover...
        with self.narration(text=en_txt) as narration:
            self.play(m.Write(en), run_time=narration.duration)
        # ...but customization is possible (see the doc for more subcaption options)
        with self.narration(
            "fr",  # speech service to be used
            "bookmarks",  # aligner to be used for bookmarks
            text="Une narration consiste a utiliser un <bookmark mark='comm'/>"
            "commentaire écrit ou parlé afin de transmettre une "
            "<bookmark mark='hist'/>histoire à un public.",
            create_subcaption=True,
            subcaption_aligner_id="subcaptions",  # aligner to be used for subcaptions
        ) as narration:
            # adjust the timing with `offset` and adding to `run_time` if needed
            # here we use InterpolationAligner for bookmarks, so it is likely needed
            self.wait_until_bookmark("comm", offset=-1.5)
            self.play(
                m.FadeIn(comm), run_time=narration.duration_until_bookmark("hist") - 0.5
            )
            self.play(m.FadeIn(hist), run_time=narration.remaining_duration)
```
