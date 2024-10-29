from paramSweep.paramSweeper import ParamSweeper
import argparse

# - Todo best-effort - frágil

description = """
Genera macros a partir de un template con variables a reemplazar y los valores posibles para cada variable
Los templates están en "macroTemplates/", el output es un directorio a discreción del usuario (outputFolder)

e.g.
        mkdir tmpMacro
        python macroGenParamSweep.py \\
            --param dQMin 0.5 0.005 \\
            --param dQRel 0.001 0.01 0.005 \\
            --paramCombination cartesian \\
            --macroTemplateFilename exampleB5_singleBeam_verbose.in \\
            --outputFolder tmpMacros
"""

parser = argparse.ArgumentParser(
    description=description, formatter_class=argparse.RawTextHelpFormatter
)

parser.add_argument("--param", dest="param", action="append", nargs="+", required=True)

parser.add_argument(
    "--paramCombination",
    dest="paramCombination",
    choices=["cartesian", "ordered"],
    help="'ordered' matches param values by index, all params must have the same number of values",
    required=True,
)

parser.add_argument(
    "--macroTemplateFilename", dest="macroTemplateFilename", required=True
)

parser.add_argument("--outputFolder", dest="outputFolder", required=True)

args = parser.parse_args()

outputFolder = args.outputFolder
macroTemplateFilename = args.macroTemplateFilename
paramArrayArray = args.param
paramCombination = args.paramCombination

paramsNameValuesDict = {
    paramName: paramValues for paramName, *paramValues in paramArrayArray
}

print("---------------------------")
print("Macro param sweeper")
print(f"Macro output folder: {outputFolder}")
for paramName, paramValues in paramsNameValuesDict.items():
    print(f"Param '{paramName} -> {paramValues}'")
print("---------------------------")

sweeper = ParamSweeper(
    macroTemplateFilename=macroTemplateFilename,
    outputMacroDir=outputFolder,
    paramsNameValuesDict=paramsNameValuesDict,
    paramCombination=paramCombination,
)

sweeper.sweep()
