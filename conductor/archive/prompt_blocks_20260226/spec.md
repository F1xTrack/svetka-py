# Specification: Prompt Blocks Library (Ultimate Edition)

## Overview
Create a massive library of 300+ prompt blocks for the Svetka-py personality constructor. This library will allow users to build unique AI personalities using a modular drag-and-drop system.

## Functional Requirements
- **Content Volume:** 300+ unique prompt blocks.
- **Categorization:** Blocks must be organized into 10+ categories (Roles, Styles, Behaviors, Constraints, Intelligence, Humor, Habits, Context, Tone, etc.).
- **Storage:** Modular JSON structure (multiple files in `assets/prompt_blocks/`) for better maintainability.
- **Dynamic Content:** Full support for `{{tags}}`, conditional logic, and nested block references.
- **UI Integration:** Blocks must be automatically detected and loaded into the `PersonalityTab` component.

## Non-Functional Requirements
- **Consistency:** All blocks must maintain a consistent tone within their respective categories.
- **Localization:** Primary language is Russian, with specialized slang/jargon where appropriate.

## Acceptance Criteria
- 300+ valid JSON blocks across modular files.
- Successful automated validation of all variables/tags.
- UI displays all categories and allows searching through all 300+ blocks.
- Manual verification of a 10% sample (30 blocks) passed.

## Out of Scope
- Implementation of the LLM API bridge (handled in T13/T16).
- Creation of the MD-template editor (already completed in T4).
