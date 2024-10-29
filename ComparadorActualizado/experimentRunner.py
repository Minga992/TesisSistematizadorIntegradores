from config.binaries import RunConfig
from pathlib import Path
from parsers.stdout import StdoutParser
from parsingConfig import parsingConfig
from utils.experiment import SingleMacroExperiment, MultiMacroExperiment
from config import paths
import argparse

# - Todo best-effort - en pathConfig está enchufado todo - frágil

description = """
Corredor de experimentos de G4

Hace N corridas para cada combinación binario-macro, como pueden ser el binario "exampleB5" y el macro "exampleB5_verbose.mac"
Para cada una, puede correr valgrind o perf para extraer más información
Usa como working dir "results/experimento/macro/run" para cada corrida, y deja ahí todos los archivos y resultados generados.

Se le puede pasar un único macro file o un directorio lleno de ellos vía --macroSource (en cuyo caso, se trata a cada macro como una run)
El parseo de resultados es para cada corrida + posibles agregadores a nivel experimento (e.g. promedios)
Puede correrse en "parsear resultados anteriores sin correr" con --parseOnly

e.g.
    python experimentRunner.py \\
        --experimentName probandoQSSExampleB5 \\
        --binary ../../builds/B5-release/exampleB5 \\
        --macroSource ../../builds/B5-release/exampleB5.in \\
        --numberOfRuns 5
"""

parser = argparse.ArgumentParser(
    description=description, formatter_class=argparse.RawTextHelpFormatter
)

parser.set_defaults(parseOnly=False)

parser.add_argument(
    "-e",
    "--experimentName",
    dest="experimentName",
    help="Experiment results output folder and identification",
    required=True,
)
parser.add_argument(
    "-g",
    "--geometryPath",
    dest="geometryPath",
    help="Path with the geometry used in an FSL experiment",
    default="",
)
parser.add_argument(
    "--runArgsMode",
    dest="runArgsMode",
    help="Select run arguments mode: 'B5like' (default, binary + macro) or 'B4like' (binary + cmdArgs)",
    default="B5like",
)
parser.add_argument(
    "--stringForParser",
    dest="stringForParser",
    help="Select the sentence that will help to parse the results",
    type=str,
    default="""G4 kernel has come to Quit state([\S\s]+)""",
)
parser.add_argument(
    "--noQSSOutput",
    dest="noQSSOutput",
    help="Prevents trying to parse QSS Stats from run stdout",
    action="store_true",
)
parser.add_argument(
    "--noPlots",
    dest="noPlots",
    help="Prevents auto-generating plots",
    action="store_true",
)
parser.add_argument(
    "--noPerTrackStats",
    dest="noPerTrackStats",
    help="Prevents trying to parse steps/substeps per track",
    action="store_true",
)
parser.add_argument(
    "-b", "--binary", dest="binary", help="Target binary path", required=True
)
#Importante para las macros que tengan la frase # QSS Params, sino no funca lo de los vtks y pml=)
parser.add_argument(
    "-m", "--macroSource", dest="macroSource", help="Target G4 macro", required=True
)
parser.add_argument(
    "-n",
    "--numberOfRuns",
    dest="numberOfRuns",
    help="Number of runs",
    type=int,
)
parser.add_argument(
    "--parseOnly",
    dest="parseOnly",
    help="Parse existing results (no runs)",
    action="store_true",
)

perfGroup = parser.add_mutually_exclusive_group()
perfGroup.add_argument(
    "--runWithCallgrind",
    dest="runWithCallgrind",
    help="Run experiments using Callgrind",
    action="store_true",
)
perfGroup.add_argument(
    "--runWithPerf",
    dest="runWithPerf",
    help="Run experiments using Perf",
    action="store_true",
)
perfGroup.add_argument(
    "--noSampleRun",
    dest="noSampleRun",
    help="Do not include a sample run",
    action="store_true",
)


args = parser.parse_args()

# Config
binaryPath = args.binary
experimentName = args.experimentName
macroSource = Path(args.macroSource)
runsPerExperiment = args.numberOfRuns
parseOnly = args.parseOnly
runWithCallgrind = args.runWithCallgrind
runWithPerf = args.runWithPerf
runArgsMode = args.runArgsMode
noQSSOutput = args.noQSSOutput
geometryPath = args.geometryPath
stringForParser = args.stringForParser
noSampleRun = args.noSampleRun

parsingConfig.pngPlots = not args.noPlots
parsingConfig.perTrackStats = not args.noPerTrackStats

if noQSSOutput:
    StdoutParser.parseQSSOutput = False

"""Correr experimento"""

multipleMacros = macroSource.is_dir()
experimentDir = paths.currentDir.joinpath("results").joinpath(experimentName)
runConfig = RunConfig(
    binaryPath=binaryPath,
    runWithCallgrind=runWithCallgrind,
    runWithPerf=runWithPerf,
    parseOnly=parseOnly,
    runArgsMode=runArgsMode,
    geometryPath=geometryPath,
    noSampleRun=noSampleRun,
)

if multipleMacros:
    experiment = MultiMacroExperiment(
        experimentName=experimentName,
        experimentDir=experimentDir,
        runConfig=runConfig,
        macroSource=macroSource,
        runsPerExperiment=runsPerExperiment,
        stringForParser=stringForParser,
    )
else:
    experiment = SingleMacroExperiment(
        experimentName=experimentName,
        experimentDir=experimentDir,
        runConfig=runConfig,
        macroFile=macroSource,
        runsPerExperiment=runsPerExperiment,
        stringForParser=stringForParser,
    )

if not parseOnly:
    experiment.run()

results = experiment.parseResults()
