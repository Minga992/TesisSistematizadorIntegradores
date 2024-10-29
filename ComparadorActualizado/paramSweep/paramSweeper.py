import itertools
from pathlib import Path
import shutil
import sys
from config.paths import mkdirIfMissing
from paramSweep.templater import Templater


class ParamSweeper:
    def __init__(
        self,
        macroTemplateFilename,
        outputMacroDir,
        paramsNameValuesDict,
        paramCombination,
    ):
        self.params = paramsNameValuesDict
        self.macroTemplateFilename = macroTemplateFilename
        self.paramCombination = paramCombination

        self.outputMacroDirPath = Path(outputMacroDir)

        if self.outputMacroDirPath.exists():
            if not self.outputMacroDirPath.is_dir():
                sys.exit("Output path should be a directory")
            shutil.rmtree(self.outputMacroDirPath)

        self.outputMacroDirPath = mkdirIfMissing(self.outputMacroDirPath)

    def sweep(self):
        # Hace tuplas con nombre-valor para cada uno de los N parámetros
        # e.g.  { a: [1, 2, 3], b: [4, 5] }
        #       [[(a, 1), (a, 2), (a, 3)],[(b, 4), (b, 5)]]
        nameMappedParamArrays = [
            [(name, value) for value in values] for name, values in self.params.items()
        ]
        paramCombinations = []
        if self.paramCombination == "cartesian":

            # Producto cartesiano, cada elemento de este array es una N-tupla con los "valores elegidos"
            # e.g.  [[(a, 1), (a, 2), (a, 3)],[(b, 4), (b, 5)]]
            #       [((a, 1),(b, 4)), ((a, 1),(b, 5)), ((a, 2),(b, 4)), ((a, 2),(b, 5)), ((a, 3),(b, 4)), ((a, 3),(b, 5))]
            paramCombinations = itertools.product(*nameMappedParamArrays)
        elif self.paramCombination == "ordered":
            paramCombinations = zip(*nameMappedParamArrays)
        else:
            sys.exit("Invalid param combination strategy")

        for paramIndex, paramCombination in enumerate(paramCombinations):
            outputMacroFilename = (
                self.macroTemplateFilename
                + "_"
                + "".join(
                    [
                        f"{paramName}_{paramValue}_"
                        for paramName, paramValue in paramCombination
                    ]
                )
            )
            outputMacroPath = self.outputMacroDirPath.joinpath(
                f"macro_{paramIndex}_{outputMacroFilename}"
            )
            replacements = {
                paramName: paramValue for paramName, paramValue in paramCombination
            }
            templater = Templater(
                macroTemplateFilename=self.macroTemplateFilename,
                outputMacroPath=outputMacroPath,
                replacements=replacements,
            )
            templater.writeOut()
