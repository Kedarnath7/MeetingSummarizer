import os

structure = {
    "meeting-summarizer": {
        ".env": "",
        "requirements.txt": "",
        "main.py": "",
        "app": {
            "__init__.py": "",
            "models.py": "",
            "core": {
                "__init__.py": "",
                "db.py": "",
            },
            "services": {
                "__init__.py": "",
                "ai_service.py": "",
            },
            "api": {
                "__init__.py": "",
                "meeting.py": "",
            },
        },
    }
}

def create_structure(base_path, structure_dict):
    for name, content in structure_dict.items():
        path = os.path.join(base_path, name)
        if isinstance(content, dict):
            os.makedirs(path, exist_ok=True)
            create_structure(path, content)
        else:
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)

if __name__ == "__main__":
    base_dir = os.getcwd()
    create_structure(base_dir, structure)
    print("Done")
