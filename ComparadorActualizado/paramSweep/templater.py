from config import paths
import sys

## Mega naive
## Reemplazando ${name} en las templates por value
## Chequea que no queden valores sin reemplazar nomás


class Templater:
    def __init__(
        self,
        macroTemplateFilename,
        outputMacroPath,
        replacements,
        replaceExpr=r"${%s}",
        allowUnreplaced=False,
    ):
        self.macroTemplateFilename = macroTemplateFilename
        self.outputMacro = outputMacroPath.resolve()
        self.replacements = replacements
        self.replaceExpr = replaceExpr
        self.allowUnreplaced = allowUnreplaced

        if r"%s" not in self.replaceExpr:
            sys.exit(
                f"Invalid replaceExpr for Templater: {self.replaceExpr}\t\t(must contain '%s')"
            )

        macroTemplatePath = paths.required(
            paths.macroTemplates.joinpath(macroTemplateFilename)
        ).resolve()
        with open(macroTemplatePath.resolve(), "r") as macroTemplateFile:
            self.macroTemplateContent = macroTemplateFile.read()

    def writeOut(self):
        print("")
        print(f"[Templater] Template: {self.macroTemplateFilename}")
        print(f"[Templater] ReplaceExpr: {self.replaceExpr}")
        for name, value in self.replacements.items():
            self.replace(name, value)
        print(f"[Templater] Output:")
        print(f"[Templater]     {self.outputMacro.name}")
        # Naive check, nomás la primera parte de replaceExpr, previo al %
        if (
            not self.allowUnreplaced
            and self.replaceExpr.partition("%")[0] in self.macroTemplateContent
        ):
            sys.exit(
                f"Falta reemplazar alguna variable en:\n\n{self.macroTemplateContent}"
            )
        with open(self.outputMacro, "w") as outMacroFile:
            outMacroFile.write(self.macroTemplateContent)

    def replace(self, varName, varValue):
        print(f"[Templater]         {varName} --> {varValue}")
        self.macroTemplateContent = self.macroTemplateContent.replace(
            self.getReplaceToken(varName), varValue
        )

    def getReplaceToken(self, varName):
        return self.replaceExpr % varName
