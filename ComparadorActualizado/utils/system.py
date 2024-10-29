import os
import subprocess
from config.paths import experimentResults


def run(runString, outputStdoutFile, runDir):
    with open(outputStdoutFile, "wb") as out:
        subprocess.run(
            runString.split(" "),
            env={**os.environ},
            stdout=out,
            cwd=f"{runDir.resolve()}",
        )


# Callgrind run:
# LD_BIND_NOW=y valgrind --tool=callgrind --instr-atstart=no ./exampleN02 ../perfMacros/n02-default-verbose.mac
def callgrindRun(
    runString, outputCallgrindFile, outputStdoutFile, outputDotFile, runDir
):
    with open(outputStdoutFile, "wb") as out:
        # perf record
        subprocess.run(
            [
                "valgrind",
                "--tool=callgrind",
                "--instr-atstart=yes",  # default yes
                f"--callgrind-out-file={outputCallgrindFile.resolve()}",
                runString,
            ],
            env={**os.environ, "LD_BIND_NOW": "y"},
            stdout=out,
            # stderr=subprocess.DEVNULL,  # Si no nos importa leer esto
            cwd=f"{runDir.resolve()}",
        )
    # https://github.com/jrfonseca/gprof2dot
    with open(outputDotFile, "wb") as out:
        gprof2dot = subprocess.Popen(
            [
                "python3",
                experimentResults.joinpath("gprof2dot.py").resolve(),
                "--format",
                "callgrind",
                # "--root",  # Deja del nodo indicado para abajo
                # "G4SteppingManager::Stepping()",
                # "--edge-thres",  # Filtra edges con menos del % indicado
                # "1",
                outputStdoutFile.resolve(),
            ],
            stdout=out,
            cwd=f"{runDir.resolve()}",
        )
        gprof2dot.wait()


# 1. Sampleo corriendo nuestra aplicación:
#       perf record -freq=997 --call-graph=dwarf --quiet --output <nombre>.data
def perfRecord(runString, outputPerfFile, outputStdoutFile, runDir):

    with open(outputStdoutFile, "wb") as out:
        # perf record
        subprocess.run(
            [
                "perf",
                "record",
                "--freq=997",
                "--call-graph=dwarf",
                "--quiet",
                "--output",
                outputPerfFile,
                runString,
            ],
            env=os.environ.copy(),
            stdout=out,
            # stderr=subprocess.DEVNULL,  # Si no nos importa leer esto
            cwd=f"{runDir.resolve()}",
        )


# 2. Perf script pipeado a el demangling de funciones de C++, luego gprof2dot para pasarlo a .dot (formato de GraphViz vectorial)
#       perf script | c++filt | gprof2dot -z G4PropagatorInField::ComputeStep --edge-thres=1 -f perf > <nombre>.dot
def perfScriptGenerateDot(outputPerfFile, outputDotFile, runDir):
    # perf script
    perfScript = subprocess.Popen(
        [
            "perf",
            "script",
            "--input",
            outputPerfFile,
        ],
        stdout=subprocess.PIPE,
        cwd=f"{runDir.resolve()}",
    )
    # c++filt
    cFilt = subprocess.Popen(
        ["c++filt"],
        stdin=perfScript.stdout,
        stdout=subprocess.PIPE,
        cwd=f"{runDir.resolve()}",
    )
    # https://github.com/jrfonseca/gprof2dot
    with open(outputDotFile, "wb") as out:
        gprof2dot = subprocess.Popen(
            [
                "python3",
                experimentResults.joinpath("gprof2dot.py").resolve(),
                "--format",
                "perf",
                # "--root",  # Deja del nodo indicado para abajo
                # "G4SteppingManager::Stepping",
                # "--edge-thres",  # Filtra edges con menos del % indicado
                # "1",
            ],
            stdin=cFilt.stdout,
            stdout=out,
            cwd=f"{runDir.resolve()}",
        )
        gprof2dot.wait()


# 3. Adicionalmente convertimos a .png para fácil chusmeo:
#       dot -Tpng -o <nombre>.png <nombre>.dot
def dotToPng(outputDotFile, outputPngFile, runDir):
    subprocess.run(
        ["dot", "-Tpng", "-o", outputPngFile, outputDotFile],
        env=os.environ.copy(),
        cwd=f"{runDir.resolve()}",
    )


# Ocupan mucho espacio los .data - los zipeamos y deleteamos el original (e.g. 200MB -> 10MB)
def compressAndDelete(input, output, runDir):
    if not input.exists():
        return

    relInput = input.name  # Prevents ugly in-zip pathing
    print(
        f"""compressAndDelete
            dir: {runDir}
            relInput: {relInput}
            output: {output}
    """
    )
    subprocess.run(
        ["zip", "-r", output, relInput],
        cwd=f"{runDir.resolve()}",
    )
    input.unlink()
