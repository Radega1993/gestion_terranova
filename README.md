# Descripción del proyecto, cómo instalarlo, usarlo, etc.

1. Crea un Entorno Virtual
```bash
python3 -m venv venv
```

2. Activar el Entorno Virtual
```bash
source venv/bin/activate
```
3. Desactivar el Entorno Virtual
```bash
deactivate
```

4. Instalar requirements
```bash
pip install -r requirements.txt
```

5. Iniciar proyecto
```bash
python -m app.gui.main_window
```


compilar release
```bash
pyinstaller --onefile --windowed --name "GestionTerranova" app/main.py
```