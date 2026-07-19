# Prompt Engineering & LLM Gateway Ledgers - BrahmaVidya Galaxy

This folder holds verified, system-vetted prompt templates and JSON Schema structures utilized by the **Vidya AI Gateway** on the application backend.

## Directory Structure & Purpose

- **`syllabus_generation/`**: Templates instructing LLM models to compile recursive educational course hierarchies (Degree -> Course -> Lesson -> Task) using strictly validated formats.
- **`quiz_generation/`**: Prompts guiding models to output complete multiple-choice assessments dynamically mapped to active lesson content descriptions.
- **`assistant_chat/`**: Guidelines framing the academic persona, boundary safety guards, and teaching constraints for our Interactive Chat Assistant.

---

## Prompt Governance Standard
To prevent drift, LLM responses must conform strictly to JSON Schema templates. Prompt parameters (such as `{topic}`, `{lesson_text}`) are combined at runtime, keeping core business parameters clean and isolated.
