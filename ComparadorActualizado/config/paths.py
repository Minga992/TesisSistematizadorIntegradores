from pathlib import Path
import sys


def required(path):
    if not path.exists():
        sys.exit(f"Not found: {path.resolve()}")
    return path


def mkdirIfMissing(path):
    if not path.exists():
        path.mkdir()
    return path


# Juntemos toda las convenciones, potencial ranciedad y cuestiones administrativas acá así el resto es más o menos feliz
# Obliguemos a correr desde root/experimentos
currentDir = Path.cwd()
if not str(currentDir).endswith("/experimentos"):
    sys.exit("Correr estas cosas desde repoRoot/experimentos")

# Seteemos los paths base
repoRoot = Path("..")

# Acá van a ir los resultados / mediciones
experimentResults = mkdirIfMissing(
    currentDir.joinpath("results")
)

macroTemplates = mkdirIfMissing(
    currentDir.joinpath("macroTemplates")
)
