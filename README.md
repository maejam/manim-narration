# Speech services

| Service   | type    | Languages              | Inference time (cpu)   | Audio sample                                               |
|-----------|---------|------------------------|------------------------|------------------------------------------------------------|
| Coqui*    | Offline | 1100+                  | 0.79 seconds           | [sample](benchmarks/narrations/CoquiService.wav?raw=True)  |
| GTTS      | Online  | en/fr/zh/pt/es         | 0.61 seconds           | [sample](benchmarks/narrations/GTTSService.wav?raw=True)   |
| Kokoro    | Offline | en/jp/zh/es/fr/hi/it/pt| 2.28 seconds           | [sample](benchmarks/narrations/KokoroService.wav?raw=True) |

*Coqui provides 70+ tts models. The one being benchmarked here is "your_tts"
