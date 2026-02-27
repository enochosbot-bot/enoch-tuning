# Qwen3-TTS-12Hz-1.7B-CustomVoice

**Source:** https://huggingface.co/Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice
**Saved:** 2026-02-15

## Overview
Qwen3-TTS is a family of text-to-speech models from Qwen covering 10 languages (Chinese, English, Japanese, Korean, German, French, Russian, Portuguese, Spanish, Italian). Uses a discrete multi-codebook LM architecture — no DiT, fully end-to-end.

## Key Features
- **12Hz tokenizer** — efficient acoustic compression with high-fidelity reconstruction
- **End-to-end architecture** — bypasses traditional LM+DiT cascading errors
- **Extreme low-latency streaming** — dual-track hybrid architecture, first audio packet after single character input, 97ms end-to-end latency
- **Instruction-driven voice control** — natural language instructions control timbre, emotion, prosody

## Model Variants
| Model | Features | Streaming | Instruction Control |
|-------|----------|-----------|-------------------|
| 1.7B-VoiceDesign | Voice design from text descriptions | ✅ | ✅ |
| 1.7B-CustomVoice | Style control over 9 premium timbres | ✅ | ✅ |
| 1.7B-Base | 3-second voice clone, fine-tuning base | ✅ | — |
| 0.6B-CustomVoice | 9 premium timbres (smaller) | ✅ | — |
| 0.6B-Base | Voice clone + FT base (smaller) | ✅ | — |

## CustomVoice Speakers (9 total)
- **Vivian** — Bright, edgy young female (Chinese)
- **Serena** — Warm, gentle young female (Chinese)
- **Uncle_Fu** — Low, mellow seasoned male (Chinese)
- **Dylan** — Youthful Beijing male (Beijing Dialect)
- **Eric** — Lively Chengdu male (Sichuan Dialect)
- **Ryan** — Dynamic male with rhythmic drive (English)
- **Aiden** — Sunny American male (English)
- **Ono_Anna** — Playful Japanese female (Japanese)
- **Sohee** — Warm Korean female (Korean)

## Setup
```bash
conda create -n qwen3-tts python=3.12 -y
conda activate qwen3-tts
pip install -U qwen-tts
pip install -U flash-attn --no-build-isolation  # optional, needs compatible GPU
```

## Usage (CustomVoice)
```python
import torch, soundfile as sf
from qwen_tts import Qwen3TTSModel

model = Qwen3TTSModel.from_pretrained(
    "Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice",
    device_map="cuda:0", dtype=torch.bfloat16,
    attn_implementation="flash_attention_2",
)

wavs, sr = model.generate_custom_voice(
    text="Hello world",
    language="English",
    speaker="Ryan",
    instruct="Speak with excitement",
)
sf.write("output.wav", wavs[0], sr)
```

## Notes
- Requires GPU with FlashAttention 2 support for best performance
- Each speaker can speak any supported language, but native language gives best quality
- Also supports voice cloning (Base models) with just 3 seconds of reference audio
- vLLM deployment supported
