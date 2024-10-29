import shutil
from paramSweep.templater import Templater
from utils import system
import sys

from utils.experimentResults import ExperimentRunResults


class ExperimentRun:

    runId = 0

    @classmethod
    def getRunId(cls):
        currentId = cls.runId
        cls.runId += 1
        return currentId

    def __init__(
        self, runConfig, macroFile, experimentDir, stringForParser, sampleRun=False
    ):

        self.sampleRun = sampleRun
        self.stringForParser = stringForParser
        if sampleRun:
            self.runId = -1
            self.runName = f"aSampleRun"
        else:
            self.runId = ExperimentRun.getRunId()
            self.runName = f"run{str(self.runId).zfill(2)}"

        self.runOutputDir = experimentDir.joinpath(self.runName)

        self.binaryFile = runConfig.binaryPath.resolve()
        self.geometryFile = runConfig.geometryPath.resolve()
        self.runWithCallgrind = runConfig.runWithCallgrind
        self.runWithPerf = runConfig.runWithPerf
        self.originalMacroFile = macroFile
        self.runConfig = runConfig

        self.outputMacroFile = self.runOutputDir.joinpath(self.originalMacroFile.name)
        self.outputCallgrindFile = self.runOutputDir.joinpath("callgrind.out").resolve()
        self.outputCallgrindDotFile = self.runOutputDir.joinpath(
            "callgrind.dot"
        ).resolve()
        self.outputPerfFile = self.runOutputDir.joinpath("perf.data").resolve()
        self.outputPerfFileZip = self.runOutputDir.joinpath("perf.zip").resolve()
        self.outputPerfDotFile = self.runOutputDir.joinpath("perf.dot").resolve()
        self.outputPngFile = self.runOutputDir.joinpath("perf.png").resolve()
        self.outputStdoutFile = self.runOutputDir.joinpath("run.out").resolve()

        self.results = None

    def run(self):
        print(f"\n> {self.runName}")
        self.runOutputDir.mkdir()

        if not self.binaryFile.exists():
            sys.exit(f"Binario no encontrado: {self.binaryFile}")

        if not self.originalMacroFile.exists():
            sys.exit(f"Macro no encontrado: {self.originalMacroFile}")

        if self.runConfig.runArgsMode == "FSLlike" and not self.geometryFile.exists():
            sys.exit(f"Geometría no encontrada: {self.geometryFile}")

        macroFileCopy = self.runOutputDir.joinpath(self.originalMacroFile.name)
        runString = self.runConfig.runStringFor(
            binaryPath=self.binaryFile,
            macroPath=macroFileCopy,
            geometryPath=self.geometryFile,
        )

        if self.sampleRun:
            # Patch cabeza para sample run
            Templater(
                macroTemplateFilename=self.originalMacroFile,
                outputMacroPath=macroFileCopy,
                replaceExpr=r"# QSS Params%s",
                replacements={"": "# QSS Params\n/QSS/generateVTKs"},
                allowUnreplaced=True,
            ).writeOut()
        else:
            shutil.copyfile(self.originalMacroFile, macroFileCopy)

        if self.runWithCallgrind:
            system.callgrindRun(
                runString=runString,
                outputCallgrindFile=self.outputCallgrindFile,
                outputStdoutFile=self.outputStdoutFile,
                outputDotFile=self.outputCallgrindDotFile,
                runDir=self.runOutputDir,
            )
        elif self.runWithPerf:
            system.perfRecord(
                runString=runString,
                outputPerfFile=self.outputPerfFile,
                outputStdoutFile=self.outputStdoutFile,
                runDir=self.runOutputDir,
            )

            system.perfScriptGenerateDot(
                self.outputPerfFile, self.outputPerfDotFile, self.runOutputDir
            )
            system.compressAndDelete(
                self.outputPerfFile, self.outputPerfFileZip, self.runOutputDir
            )
            system.dotToPng(
                self.outputPerfDotFile, self.outputPngFile, self.runOutputDir
            )
        else:
            system.run(
                runString=runString,
                outputStdoutFile=self.outputStdoutFile,
                runDir=self.runOutputDir,
            )

        self.results = self.parseResults()

    def parseResults(self):
        if not self.results:
            self.results = ExperimentRunResults(experimentRun=self)
        return self.results
