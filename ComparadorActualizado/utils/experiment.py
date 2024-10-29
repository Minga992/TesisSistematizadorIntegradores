from abc import abstractmethod
from utils.experimentResults import (
    MultiMacroExperimentResults,
    SingleMacroExperimentResults,
)
from utils.experimentRun import ExperimentRun
import sys


class BaseExperiment:
    def __init__(
        self,
        experimentName,
        experimentDir,
        runConfig,
        runsPerExperiment,
        stringForParser,
    ):
        self.runConfig = runConfig
        self.experimentDir = experimentDir
        self.experimentName = experimentName
        self.sampleRun = None
        self.runsPerExperiment = runsPerExperiment
        self.stringForParser = stringForParser
        self.runs = []
        if not runConfig.parseOnly:
            # Crear root dir del experimento - si ya existe explota para evitar pisar resultados
            if self.experimentDir.exists():
                sys.exit(
                    f"Ya existe un experimento con ese nombre ({self.experimentDir})"
                )
            else:
                self.experimentDir.mkdir()

    @abstractmethod
    def runMessage(self):
        pass

    def run(self):
        self.runMessage()
        if self.sampleRun:
            print("-- Executing sample run --")
            self.sampleRun.run()
        for experiment in self.runs:
            experiment.run()

    @abstractmethod
    def experimentDescription(self):
        pass

    @abstractmethod
    def parseResults(self):
        pass


class SingleMacroExperiment(BaseExperiment):
    def __init__(
        self,
        experimentName,
        experimentDir,
        runConfig,
        macroFile,
        runsPerExperiment,
        stringForParser,
    ):
        super().__init__(
            experimentName, experimentDir, runConfig, runsPerExperiment, stringForParser
        )
        self.macroFile = macroFile.resolve()

        if not self.runConfig.noSampleRun:
            # Add sample run
            self.sampleRun = ExperimentRun(
                runConfig=self.runConfig,
                macroFile=self.macroFile,
                experimentDir=self.experimentDir,
                stringForParser=stringForParser,
                sampleRun=True,
            )

        # Single macro file - N runs
        for _ in range(self.runsPerExperiment):
            self.runs.append(
                ExperimentRun(
                    runConfig=self.runConfig,
                    macroFile=self.macroFile,
                    experimentDir=self.experimentDir,
                    stringForParser=stringForParser,
                )
            )

    def runMessage(self):
        print(
            f"""Corriendo experimento:
                                Run config:
                                    Binary: {self.runConfig.binaryPath.resolve()}
                                Macro config:
                                    Macro: {self.macroFile.name}
                                    RunsPerMacro: {self.runsPerExperiment}
                    """
        )

    def experimentDescription(self):
        return f"[{self.runs[0].runId}, {self.runs[-1].runId}]\t{self.macroFile.name}"

    def parseResults(self):
        return SingleMacroExperimentResults(experiment=self)


class MultiMacroExperiment(BaseExperiment):
    def __init__(
        self,
        experimentName,
        experimentDir,
        runConfig,
        macroSource,
        runsPerExperiment,
        stringForParser,
    ):
        super().__init__(
            experimentName, experimentDir, runConfig, runsPerExperiment, stringForParser
        )
        self.macroSource = macroSource.resolve()
        self.macroFiles = [
            macroFilePath.resolve() for macroFilePath in sorted(macroSource.glob("*"))
        ]
        # Multiple macro files - N runs each - cada macro es un Experiment, con sus N runs adentro
        for macro in self.macroFiles:
            macroRunsDir = self.experimentDir.joinpath(macro.name)
            self.runs.append(
                SingleMacroExperiment(
                    experimentName=macro.name,
                    experimentDir=macroRunsDir,
                    runConfig=self.runConfig,
                    macroFile=macro,
                    runsPerExperiment=self.runsPerExperiment,
                    stringForParser=stringForParser,
                )
            )

    def runMessage(self):
        print(
            f"""Corriendo experimento - multiples macros desde {self.macroSource}:
                        Run config:
                            Binary: {self.runConfig.binaryPath.resolve()}
                        Macro config:
                            Macros: {len(self.macroFiles)} files
                            RunsPerMacro: {self.runsPerExperiment}
            """
        )

    def experimentDescription(self):
        return "\n".join(
            [experiment.experimentDescription() for experiment in self.runs]
        )

    def parseResults(self):
        return MultiMacroExperimentResults(experiment=self)
