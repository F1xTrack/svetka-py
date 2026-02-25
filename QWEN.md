# Project Overview: Svetka-py

## Purpose
**Svetka-py** is a highly flexible, proactive AI companion for Windows. It integrates into the user's workspace, analyzing visual (screen) and auditory (microphone/system audio) context in real-time. The bot possesses its own "desire" to speak, providing commentary and engagement based on the user's actions and emotional state.

## Core Technologies
- **Language:** Python 3.10+ (using `asyncio` for real-time operations).
- **GUI:** PyQt6 / PySide6 (featuring a hybrid approach with a browser-based mini-client for modern design).
- **Vision:** MSS for high-speed screen capture, OpenCV for processing, and VLM (Vision Language Models) for context understanding.
- **Audio:** Sounddevice / PyAudio for microphone and system loopback capture. Supports both STT -> LLM and native multimodal audio input (e.g., Gemini 2.0+).
- **AI Integration:** Universal bridge supporting OpenAI, Gemini, and Claude API schemes via `base_url` customization.
- **Memory:** RAG (Retrieval-Augmented Generation) combined with smart context compression (summarizing history after 400k+ tokens while preserving the last 10 interactions).

## Architecture & Management
The project follows the **Conductor** methodology, organized into "Tracks" (high-level work units).
- **Configuration:** Centrally managed via `ConfigManager` using YAML with hierarchical structures and support for 50+ parameters.
- **Project Context:** All definitions and workflows are stored in the `conductor/` directory.
- **Track Management:** Tracks are registered in `conductor/tracks.md` and detailed in `conductor/tracks/<track_id>/`.

## Development Workflow & Conventions
- **Language of Communication:** The AI agent MUST communicate with the user exclusively in **Russian**.
- **Testing:** Mandatory 95% code coverage.
- **CI/CD:** Automated testing and release building via GitHub Actions.
- **Git Protocol:** Commits are made after each phase of development. Task summaries are recorded in both Git Notes and commit message bodies.
- **Style:** Adheres to the Python style guide defined in `conductor/code_styleguides/python.md`.
- **Concurrency:** Extensive use of `asyncio` to prevent UI freezing during AI inference and data capture.

## Running & Building
- **Environment:** Managed via **Poetry** for strict dependency control.
- **Build:** Packaged into a single Windows `.exe` using **PyInstaller**.
- **Commands:**
  - `poetry run python main.py` - Run the application.
  - `poetry run pytest` - Run the test suite (requires AITunnel API key for certain tests).
  - `poetry run pyinstaller svetka.spec` - Build the executable.

## Project Structure
- `/ui` - PyQt6/Browser hybrid interface files.
- `/core` - Central logic, including `ConfigManager`, `APIBridge`, and `ContextManager`.
- `/modules` - Specialized AI modules (Vision, Audio, Personality, Memory).
- `/assets` - Templates, prompt blocks, and resource files.
- `/tests` - Pytest suite and visual test data (.webm files).
- `/conductor` - Conductor framework metadata and project definition.
