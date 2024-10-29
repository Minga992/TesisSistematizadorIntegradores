import json
import csv
from parsers.dotfile import DotfileParser
from parsers.stdout import StdoutParser
from utils.functions import (
    flatten,
    statsOfValues,
)
from utils.system import compressAndDelete
from parsingConfig import parsingConfig


class ExperimentRunResults:
    def __init__(self, experimentRun):
        self.experimentRun = experimentRun
        self.runId = experimentRun.runId
        self.stringForParser = experimentRun.stringForParser
        self.dotfileResults = (
            DotfileParser().parse(file=self.experimentRun.outputPerfDotFile)
            if self.experimentRun.runWithPerf
            else {}
        )
        self.stdoutResults = StdoutParser().parse(
            file=self.experimentRun.outputStdoutFile,
            stringForParser=self.stringForParser,
        )

        self.printOut()
        self.compressAndDeleteOutfiles()

    def compressAndDeleteOutfiles(self):
        # Los .out son enormes en experimentos grandes, si ya parseé lo que me interesa y pesa más de N MB, zipeo
        if (
            self.experimentRun.outputStdoutFile.exists()
            and self.experimentRun.outputStdoutFile.stat().st_size > 2 * 1024 * 1024
        ):
            compressAndDelete(
                self.experimentRun.outputStdoutFile,
                f"{self.experimentRun.outputStdoutFile}.zip",
                self.experimentRun.runOutputDir,
            )

    def printOut(self):
        statsOut = {
            "runId": self.experimentRun.runId,
            "dotfile": {**self.dotfileResults},
            "stdout": {**self.stdoutResults},
        }
        with open(
            self.experimentRun.runOutputDir.joinpath("stats.out"), "w"
        ) as outStats:
            outStats.write(json.dumps(statsOut, indent=4, sort_keys=True))


class SingleMacroExperimentResults:
    def __init__(self, experiment):
        self.experiment = experiment
        self.experimentCsvDataRow = []
        print(self.experiment.experimentName)
        print("[SingleMacroExperimentResults]\tParsing run results...")
        self.runResults = [
            experimentRun.parseResults() for experimentRun in self.experiment.runs
        ]
        self.runIds = [runResult.runId for runResult in self.runResults]

        print("[SingleMacroExperimentResults]\tCalculating aggregated results...")
        self.aggregatedExperimentResults = self.calculateAggregatedResults()

        self.printOut()

        print("[SingleMacroExperimentResults]\tPlotting aggregated results...")

        if parsingConfig.pngPlots:
            self.plotAggregatedResults()

    def calculateAggregatedResults(self):
        aggregatedDotfileResults = DotfileParser().aggregateRunResults(
            [runResult.dotfileResults for runResult in self.runResults]
        )
        aggregatedStdoutResults = StdoutParser().aggregateRunResults(
            [runResult.stdoutResults for runResult in self.runResults]
        )

        self.makeCsvParams(aggregatedStdoutResults, StdoutParser.parseQSSOutput)

        return {**aggregatedDotfileResults, **aggregatedStdoutResults}

    def printOut(self):
        jsonPrint(
            outputFile=self.experiment.experimentDir.joinpath("stats.out"),
            content=self.aggregatedExperimentResults,
        )

    def plotAggregatedResults(self):
        imgsDir = self.experiment.experimentDir.joinpath("imgs")
        StdoutParser().plotAggregatedResults(
            aggregatedResults=self.aggregatedExperimentResults,
            runIds=self.runIds,
            imgsDir=imgsDir,
        )

    # This depends strongly of what we want to show and what we are showing, if any stat is not
    # available anymore, we need to change this function.
    def makeCsvParams(self, aggregatedStdoutResults, flagQss):
        if flagQss:
            totalSteps = aggregatedStdoutResults["totalSteps"]["mean"]
            realTime = aggregatedStdoutResults["realTime"]["mean"]
            averageTimePerStep = realTime / totalSteps
            binaryName = str(self.experiment.runConfig.binaryPath)
            macroName = str(self.experiment.macroFile)
            if binaryName.rfind("/") != -1:
                binaryName = binaryName[binaryName.rfind("/")+1:]
            if macroName.rfind("/") != -1:
                macroName = macroName[macroName.rfind("/")+1:]
            self.experimentCsvDataRow.append("PutExample")
            self.experimentCsvDataRow.append("PutSubExample")
            self.experimentCsvDataRow.append("PutObs")
            self.experimentCsvDataRow.append(binaryName)
            self.experimentCsvDataRow.append(aggregatedStdoutResults["dQRel"]["mean"])
            self.experimentCsvDataRow.append(aggregatedStdoutResults["dQMin"]["mean"])
            self.experimentCsvDataRow.append("PutPhysics")
            self.experimentCsvDataRow.append(
                aggregatedStdoutResults["numberOfThreads"]["mean"]
            )
            self.experimentCsvDataRow.append(
                aggregatedStdoutResults["intersections"]["mean"]
            )
            self.experimentCsvDataRow.append(totalSteps)
            self.experimentCsvDataRow.append(
                aggregatedStdoutResults["substepAveragePerStep"]["mean"]
            )
            self.experimentCsvDataRow.append(
                aggregatedStdoutResults["userTime"]["mean"]
            )
            self.experimentCsvDataRow.append(realTime)
            self.experimentCsvDataRow.append(
                aggregatedStdoutResults["systemTime"]["mean"]
            )
            self.experimentCsvDataRow.append(averageTimePerStep)
            self.experimentCsvDataRow.append("PutProfitUserTime")
            self.experimentCsvDataRow.append("PutProfitRealTime")
            self.experimentCsvDataRow.append("PutProfitSystemTime")
            self.experimentCsvDataRow.append(macroName)
            self.experimentCsvDataRow.append("PutExperimentFolder")
        else:
            totalSteps = aggregatedStdoutResults["totalSteps"]["mean"]
            realTime = aggregatedStdoutResults["realTime"]["mean"]
            averageTimePerStep = realTime / totalSteps if totalSteps > 0 else 0
            binaryName = str(self.experiment.runConfig.binaryPath)
            macroName = str(self.experiment.macroFile)
            if binaryName.rfind("/") != -1:
                binaryName = binaryName[binaryName.rfind("/")+1:]
            if macroName.rfind("/") != -1:
                macroName = macroName[macroName.rfind("/")+1:]
            self.experimentCsvDataRow.append("PutExample")
            self.experimentCsvDataRow.append("PutSubExample")
            self.experimentCsvDataRow.append("PutObs")
            self.experimentCsvDataRow.append(binaryName)
            self.experimentCsvDataRow.append("N/A")
            self.experimentCsvDataRow.append("N/A")
            self.experimentCsvDataRow.append("PutPhysics")
            self.experimentCsvDataRow.append(
                aggregatedStdoutResults["numberOfThreads"]["mean"]
            )
            self.experimentCsvDataRow.append(
                aggregatedStdoutResults["intersections"]["mean"]
            )
            self.experimentCsvDataRow.append(totalSteps)
            self.experimentCsvDataRow.append("N/A")
            self.experimentCsvDataRow.append(
                aggregatedStdoutResults["userTime"]["mean"]
            )
            self.experimentCsvDataRow.append(realTime)
            self.experimentCsvDataRow.append(
                aggregatedStdoutResults["systemTime"]["mean"]
            )
            self.experimentCsvDataRow.append(averageTimePerStep)
            self.experimentCsvDataRow.append("N/A")
            self.experimentCsvDataRow.append("N/A")
            self.experimentCsvDataRow.append("N/A")
            self.experimentCsvDataRow.append(macroName)
            self.experimentCsvDataRow.append("PutExperimentFolder")


class MultiMacroExperimentResults:
    def __init__(self, experiment):
        self.experiment = experiment
        self.experimentCsvHeader = [
            "Example",
            "subExample",
            "Obs",
            "binary",
            "dQrel",
            "dQmin",
            "physics",
            "Number of threads",
            "intersections",
            "Total Steps",
            "Substeps per step",
            "User Time(seg)",
            "Real Time(seg)",
            "System Time(seg)",
            "Average Time per step(seg)",
            "Profit User Time vs Dopri",
            "Profit Real Time vs Dopri",
            "Profit System Time vs Dopri",
            "Macro Name",
            "Experiment Folder",
        ]
        self.experimentCsvData = []
        print(self.experiment.experimentName)

        print("[MultiMacroExperimentResults]\tParsing experiment results...")
        self.singleMacroExperimentResults = [
            experiment.parseResults() for experiment in self.experiment.runs
        ]
        self.runIds = flatten(
            [
                singleMacroExperimentResult.runIds
                for singleMacroExperimentResult in self.singleMacroExperimentResults
            ]
        )

        for singleMacroExperimentResult in self.singleMacroExperimentResults:
            self.experimentCsvData.append(
                singleMacroExperimentResult.experimentCsvDataRow
            )

        print("[MultiMacroExperimentResults]\tCalculating aggregated results...")
        self.aggregatedExperimentResults = self.calculateAggregatedResults()

        self.printOut()

        print("[MultiMacroExperimentResults]\tPlotting aggregated results...")

        if parsingConfig.pngPlots:
            self.plotAggregatedResults()

    def calculateAggregatedResults(self):
        runsPerExperiment = len(self.singleMacroExperimentResults[0].runIds)
        singleMacroExperimentAggregatedResults = [
            singleMacroExperimentResult.aggregatedExperimentResults
            for singleMacroExperimentResult in self.singleMacroExperimentResults
        ]
        aristas = set().union(
            *[
                singleMacroExperimentResult.keys()
                for singleMacroExperimentResult in singleMacroExperimentAggregatedResults
            ]
        )
        aggregatedResults = {}
        for arista in aristas:
            values = []
            units = None
            for (
                singleMacroExperimentAggregatedResult
            ) in singleMacroExperimentAggregatedResults:
                if arista in singleMacroExperimentAggregatedResult:
                    if not units:
                        units = singleMacroExperimentAggregatedResult[arista]["units"]
                    values.append(
                        singleMacroExperimentAggregatedResult[arista]["values"]
                    )
                else:
                    values.append([None for _ in range(runsPerExperiment)])
            values = flatten(values)
            aggregatedResults[arista] = statsOfValues(
                values=values, units=units, ignoreNone=True
            )
        return aggregatedResults

    def printOut(self):
        with open(
            self.experiment.experimentDir.joinpath("experiment.data"), "w"
        ) as outExpData:
            description = self.experiment.experimentDescription()
            outExpData.write(description)

        print("[About to relevant stats]\tabput to...")

        with open(
            self.experiment.experimentDir.joinpath("RelevantStats.csv"), "w", newline=""
        ) as file:
            csvwriter = csv.writer(file)
            csvwriter.writerow(self.experimentCsvHeader)
            csvwriter.writerows(self.experimentCsvData)

        print("[After relevant stats]\tafter that...")

        jsonPrint(
            outputFile=self.experiment.experimentDir.joinpath("stats.out"),
            content=self.aggregatedExperimentResults,
        )

    def plotAggregatedResults(self):
        imgsDir = self.experiment.experimentDir.joinpath("imgs")
        StdoutParser().plotAggregatedResults(
            aggregatedResults=self.aggregatedExperimentResults,
            runIds=self.runIds,
            imgsDir=imgsDir,
        )


def jsonPrint(outputFile, content):
    with open(outputFile, "w") as outStats:
        outStats.write(json.dumps(content, indent=4, sort_keys=True))
