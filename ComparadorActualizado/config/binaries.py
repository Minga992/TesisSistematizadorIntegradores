from config import paths
from pathlib import Path
import os
import sys


class RunConfig:
    def __init__(
        self,
        binaryPath,
        runWithCallgrind,
        runWithPerf,
        parseOnly,
        runArgsMode,
        geometryPath,
        noSampleRun,
    ):
        self.runWithCallgrind = runWithCallgrind
        self.runWithPerf = runWithPerf
        self.binaryPath = Path(binaryPath)
        self.parseOnly = parseOnly
        self.geometryPath = Path(geometryPath)
        self.noSampleRun = noSampleRun

        if runArgsMode not in ["B5like", "B4like", "FSLlike"]:
            sys.exit("Unklnown runArgsMode")

        self.runArgsMode = runArgsMode

        self.checkEnvVars()

    def checkEnvVars(self):
        # Si es un dry run para parsear cosas no nos importa
        if self.parseOnly:
            return
        # Cuando hacemos 'make install' en Geant4, se genera un "geant4.sh" en el INSTALL_DIR
        # que setea variables de entorno que las aplicaciones esperan (por ej. dónde están los data files)
        # Necesitamos correrlo antes de invocar a N02 / FSL
        ensdfstatedata = os.getenv("G4ENSDFSTATEDATA")
        if ensdfstatedata is None:
            scriptPath = paths.builds.joinpath(
                "$QSS_BASE/builds/geant4-dev-release/install/bin/geant4.sh"
            )
            sys.exit(
                f"""
                Problemas con envvars. Fijate que sea la versión correcta.
                Falta correr script geant4.sh antes para setear variables correctamente, e.g.:
                    cd "{scriptPath.parent.resolve()}";
                    source "{scriptPath.resolve()}";
                    cd -
                """
            )

    def runStringFor(self, binaryPath, macroPath, geometryPath):
        # exampleB4 -t 1 -m macro
        # Setting t=1 for multithreaded mode enabled (re-set using macro when running experiments)
        if self.runArgsMode == "B4like":
            return f"{binaryPath} -m {macroPath} -t 1"
        elif self.runArgsMode == "FSLlike":
            return f"{binaryPath} -m {macroPath} -g {geometryPath}"
        return f"{binaryPath} {macroPath}"
