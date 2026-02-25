import os
import json
import re
from pathlib import Path
from datetime import datetime
from typing import Optional, List
from fastmcp import FastMCP

mcp = FastMCP("Conductor")

# Конфигурация путей
BASE_DIR = Path.cwd()
CONDUCTOR_DIR = BASE_DIR / "conductor"
TRACKS_DIR = CONDUCTOR_DIR / "tracks"
TEMPLATES_DIR = Path(os.path.expanduser("~/.gemini/extensions/conductor/templates"))

def get_setup_state():
    state_file = CONDUCTOR_DIR / "setup_state.json"
    if state_file.exists():
        return json.loads(state_file.read_text(encoding="utf-8"))
    return {"last_successful_step": ""}

@mcp.tool()
def conductor_get_status() -> str:
    \"\"\"Возвращает текущий статус проекта Conductor и прогресс настройки.\"\"\"
    if not CONDUCTOR_DIR.exists():
        return "Conductor не инициализирован. Используйте conductor_init_structure."
    
    state = get_setup_state()
    tracks_file = CONDUCTOR_DIR / "tracks.md"
    tracks_content = tracks_file.read_text(encoding="utf-8") if tracks_file.exists() else "Реестр треков пуст."
    
    return f"--- Статус настройки ---\nПоследний шаг: {state.get('last_successful_step')}\n\n--- Активные треки ---\n{tracks_content}"

@mcp.tool()
def conductor_init_structure() -> str:
    \"\"\"Создает базовую структуру папок проекта Conductor.\"\"\"
    try:
        CONDUCTOR_DIR.mkdir(exist_ok=True)
        TRACKS_DIR.mkdir(exist_ok=True)
        (CONDUCTOR_DIR / "code_styleguides").mkdir(exist_ok=True)
        
        state_file = CONDUCTOR_DIR / "setup_state.json"
        if not state_file.exists():
            state_file.write_text(json.dumps({"last_successful_step": ""}), encoding="utf-8")
            
        return "Структура Conductor создана успешно."
    except Exception as e:
        return f"Ошибка при создании структуры: {str(e)}"

@mcp.tool()
def conductor_write_doc(name: str, content: str, step_name: Optional[str] = None) -> str:
    \"\"\"Записывает основной документ (product, tech-stack, workflow) и обновляет состояние.\"\"\"
    try:
        file_path = CONDUCTOR_DIR / f"{name}.md"
        file_path.write_text(content, encoding="utf-8")
        
        if step_name:
            state_file = CONDUCTOR_DIR / "setup_state.json"
            state_file.write_text(json.dumps({"last_successful_step": step_name}), encoding="utf-8")
            
        return f"Документ {name}.md успешно сохранен."
    except Exception as e:
        return f"Ошибка записи документа: {str(e)}"

@mcp.tool()
def conductor_create_track(track_id: str, title: str, spec: str, plan: str, description: str) -> str:
    \"\"\"Создает новый трек со всеми артефактами (metadata, spec, plan, index).\"\"\"
    try:
        t_dir = TRACKS_DIR / track_id
        t_dir.mkdir(parents=True, exist_ok=True)
        
        # Metadata
        metadata = {
            "track_id": track_id,
            "type": "feature",
            "status": "new",
            "created_at": datetime.now().isoformat() + "Z",
            "updated_at": datetime.now().isoformat() + "Z",
            "description": description
        }
        (t_dir / "metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
        
        # Files
        (t_dir / "spec.md").write_text(spec, encoding="utf-8")
        (t_dir / "plan.md").write_text(plan, encoding="utf-8")
        (t_dir / "index.md").write_text(f"# Track {track_id} Context\n\n- [Specification](./spec.md)\n- [Implementation Plan](./plan.md)\n- [Metadata](./metadata.json)", encoding="utf-8")
        
        # Registry update
        reg_file = CONDUCTOR_DIR / "tracks.md"
        if not reg_file.exists():
            reg_file.write_text("# Project Tracks\n\n---\n", encoding="utf-8")
        
        with open(reg_file, "a", encoding="utf-8") as f:
            f.write(f"\n- [ ] **Track: {title}**\n  *Link: [./tracks/{track_id}/](./tracks/{track_id}/)*\n")
            
        return f"Трек {track_id} полностью создан."
    except Exception as e:
        return f"Ошибка при создании трека: {str(e)}"

@mcp.tool()
def conductor_update_task(track_id: str, task_name: str, completed: bool = True) -> str:
    \"\"\"Обновляет статус задачи в плане трека ([ ] -> [x]).\"\"\"
    try:
        plan_path = TRACKS_DIR / track_id / "plan.md"
        if not plan_path.exists():
            return f"План для трека {track_id} не найден."
            
        content = plan_path.read_text(encoding="utf-8")
        mark = "[x]" if completed else "[ ]"
        
        # Регулярка для поиска строки задачи
        pattern = rf"- \[ . \] Task: {re.escape(task_name)}"
        new_line = f"- {mark} Task: {task_name}"
        
        if not re.search(pattern, content):
            # Пробуем найти без префикса Task:
            pattern = rf"- \[ . \] {re.escape(task_name)}"
            new_line = f"- {mark} {task_name}"
            
        new_content = re.sub(pattern, new_line, content)
        
        if new_content == content:
            return f"Задача '{task_name}' не найдена в плане."
            
        plan_path.write_text(new_content, encoding="utf-8")
        return f"Статус задачи '{task_name}' обновлен на {mark}."
    except Exception as e:
        return f"Ошибка обновления задачи: {str(e)}"

@mcp.tool()
def conductor_get_templates() -> str:
    \"\"\"Возвращает список доступных шаблонов стилей и воркфлоу из библиотеки.\"\"\"
    if not TEMPLATES_DIR.exists():
        return "Директория шаблонов не найдена."
    
    result = []
    for root, dirs, files in os.walk(TEMPLATES_DIR):
        rel_path = Path(root).relative_to(TEMPLATES_DIR)
        for f in files:
            result.append(str(rel_path / f))
    return "\n".join(result)

@mcp.tool()
def conductor_apply_styleguide(name: str) -> str:
    \"\"\"Копирует выбранный гайд в проект.\"\"\"
    try:
        src = TEMPLATES_DIR / "code_styleguides" / f"{name}.md"
        dst = CONDUCTOR_DIR / "code_styleguides" / f"{name}.md"
        if src.exists():
            dst.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
            return f"Гайд {name} скопирован."
        return f"Гайд {name} не найден в библиотеке."
    except Exception as e:
        return str(e)

@mcp.tool()
def conductor_get_track_context(track_id: str) -> str:
    \"\"\"Загружает спецификацию и план конкретного трека для контекста модели.\"\"\"
    try:
        t_dir = TRACKS_DIR / track_id
        if not t_dir.exists():
            return f"Трек {track_id} не найден."
        
        spec = (t_dir / "spec.md").read_text(encoding="utf-8")
        plan = (t_dir / "plan.md").read_text(encoding="utf-8")
        
        return f"--- SPECIFICATION ---\n{spec}\n\n--- IMPLEMENTATION PLAN ---\n{plan}"
    except Exception as e:
        return f"Ошибка загрузки контекста трека: {str(e)}"

if __name__ == "__main__":
    mcp.run()
