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
- Skip the rendering of narrations globally via config options or per section (e.g. `self.next_section(skip_narrations=True, skipped_narrations_duration=5.0)`)
- Generate multiple narrations at once in multiple threads for much better performance.

Missing features:
- recording service
- translation


### Available speech services

Check the `benchmarks/` directory to see how those statistics are produced. You can also run the benchmark scripts on your setup.

| Service    | type   | Languages              | Inference time (cpu)* | Audio sample                                               |
|------------|--------|------------------------|-----------------------|------------------------------------------------------------|
| Coqui\*\*  | Local  | 1100+                  | 5.27 / 2.83           | [sample](benchmarks/narrations/Coqui.wav?raw=True)         |
| GTTS       | Online | en/fr/zh/pt/es         | 0.58 / 0.18           | [sample](benchmarks/narrations/GTTS.wav?raw=True)          |
| Kokoro     | Local  | en/jp/zh/es/fr/hi/it/pt| 1.23 / 0.49           | [sample](benchmarks/narrations/Kokoro.wav?raw=True)        |
| Chatterbox | Local  | 23 languages           | 31.37 / 19.74         | [sample](benchmarks/narrations/Chatterbox.wav?raw=True)    |

<sub>\*Mean time in seconds to generate 10 short speeches (sequential / multithreading (3 workers))</sub>  
<sub>\*\*Coqui provides 70+ tts models. The one being benchmarked here is "xtts_v2"</sub>  

> [!NOTE]
> multiprocessing is also available but is unstable with some speech services and MUCH longer anyway.  


### Available alignment services

The role of the `aligners` is to match up the text spoken in the generated audio file with the moment it is spoken. They are only useful when using bookmarks or for synchronizing subcaptions.

| Service       | Description                                          | type  | Inference time (cpu)   | Distance from truth |
|---------------|------------------------------------------------------|-------|------------------------|---------------------|
| Manual        | Lets the user manually align text and speech         | Local | 0.0 seconds            |          irrelevant |
| Interpolation | timestamp = audio_duration * char_offset / len(text) | Local | 0.0 seconds            |                3.24 |
| CTC*          | Let a CTC model from HuggingFace do the alignment    | Local | 13.02 seconds          |                0.18 |

<sub>*pretrained Wav2Vec2, HuBERT, and MMS models from HuggingFace can be used. The one being benchmarked here is the default model (https://huggingface.co/MahmoudAshraf/mms-300m-1130-forced-aligner)</sub>

> [!NOTE]
> Running local services for the first time will trigger the download of the models. This can be a lengthy process but the models are then cached.


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
For now there is no dedicated documentation. See the in-code documentation and the `examples/` directory.


## Example

> [!IMPORTANT]
> Just like `manim-voiceover`, render scenes with `--disable_caching` to avoid bugs.  

> [!NOTE]
> The example below uses `GTTSService`. To run it you must install with `gtts` extra.  

<sub>Activate the sound under the video.</sub>

https://github.com/user-attachments/assets/d08047e7-b19a-425b-9d04-f3fbb0632add

```python
from manim import *

from manim_narration import NarrationScene
from manim_narration.speech import GTTSService


class GettingStarted(NarrationScene):
    def construct(self) -> None:
        # define speech service(s) with a name
        self.set_speech_services(
            en=GTTSService(lang="en"),
            fr=GTTSService(lang="fr"),
        )

        en_txt = (
            "Narration is the use of a written or spoken \n"
            "commentary to convey a story to an audience."
        )
        fr_txt = (
            "Une narration consiste a utiliser un commentaire écrit ou parlé \n"
            "afin de transmettre une histoire à un public."
        )

        # The first argument to the context manager is the speech service to use.
        # If ommited, it will default to the first one defined in set_speech_services.
        with self.narration(text=en_txt) as narration:
            self.play(
                FadeIn(Text(en_txt, font_size=30).shift(UP)),
                run_time=narration.duration,
            )

        # To use any other speech service, pass its name as the first argument.
        with self.narration(
            "fr",
            text=fr_txt,
            create_subcaption=True,
        ) as narration:
            self.play(
                Write(Text(fr_txt, font_size=30).shift(DOWN)),
                run_time=narration.duration,
            )
```

See more examples in the `examples/` directory.
