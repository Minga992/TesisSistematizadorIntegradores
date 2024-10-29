from ast import literal_eval
from parsers.stdoutParams.nonQss import NonQSS
from parsers.stdoutParams.runParams import RunParams
from parsers.stdoutParams.stepCount import StepCount
from parsers.stdoutParams.time import Time
from parsers.stdoutParams.varChanges import VarChanges
from parsers.utils import searchAndGetMatch
from utils.graficador import Graficador
from collections import ChainMap


# Parsing 100% output dependant, si cambian QSS Stats -> hay que actualizar esto
class StdoutParser:

    # Cuando corremos DOPRI no parseemos nada de QSS
    parseQSSOutput = True

    def __init__(self):
        self.stdoutParams = [NonQSS()]
        if StdoutParser.parseQSSOutput:
            self.stdoutParams.extend([RunParams(), StepCount(), Time(), VarChanges()])

    # Mega naive regex parse de lo que nos interesa.
    def parse(self, file, stringForParser):
        try:
            with open(file, "r") as f:
                content = f.read()

                print(f"Parsing {file}")

                # Encontrar un string de "finalización" parece medio tricky, mucho de lo que fuimos levantando
                # corresponde específicamente a ejemplos, o a levantar visualización, o cosas de multithreading.
                # El "G4 kernel has come to Quit state" parece ocurrir cuando cualquier thread termina, parece
                # ser suficiente para el propósito de "quedarnos con el último cacho del output".
                # sin embargo, fsl no respeta eso =)
                # para no cambiar siempre este pedazo de código, se agrego por parametro un campo que
                # permite controlando, teniendo por default el "G4 kernel... bla"
                epilogue = searchAndGetMatch(content, stringForParser)
                chunks = {
                    "stdout": content,
                    "epilogue": epilogue,
                }

                if StdoutParser.parseQSSOutput:
                    chunks["qssStats"] = searchAndGetMatch(
                        epilogue, "(QSS stats:[\S\s]+)"
                    )

                res = ChainMap(
                    *[param.parse(chunks=chunks) for param in self.stdoutParams]
                )

                print(
                    f"""
                    STDOUT RESULTS
                        {res}"""
                )
                return res
        except FileNotFoundError:
            print("-- no stdout file, using stats.out -- ")
            statsOutFile = file.parent.joinpath("stats.out")
            with open(statsOutFile, "r") as f:
                res = literal_eval(f.read())["stdout"]
                return res

    def aggregateRunResults(self, results):
        res = ChainMap(
            *[param.aggregateRunResults(results) for param in self.stdoutParams]
        )
        return res

    def plotAggregatedResults(self, aggregatedResults, runIds, imgsDir):
        graficador = Graficador(outputImgsDir=imgsDir)
        # Alternativa cabeza fácil temporal "mandale a todo"
        for arista in aggregatedResults:

            # Generar gráficos únicamente para track 1 por default
            # No es info. útil a priori para generar cientos
            if "track_" in arista and not "track_1_" in arista:
                continue

            results = aggregatedResults[arista]

            graficador.simpleCurvePlot(
                title=arista,
                xlabel="# runId",
                xvalues=runIds,
                values=results["values"],
                includeMean=True,
                ylabel=results["units"],
            )

            graficador.simpleHistogramPlot(
                title=arista,
                xlabel=results["units"],
                values=results["values"],
                ylabel="# runs",
            )

        # ToDo: Que cada param parseado grafique cosas interesantes puntuales
        # [param.plot(graficador, aggregatedResults) for param in self.stdoutParams]
