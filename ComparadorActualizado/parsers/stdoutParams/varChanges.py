from parsers.utils import searchAndGetMatch
from utils.functions import statsOfKeyInArray


class VarChanges:
    def getVariableNStuff(self, varName, qssStats):
        dQRelChanges = float(
            searchAndGetMatch(
                qssStats,
                f"Variable {varName}:[\S\s]+dQRel changes: (.+)",
            )
        )
        dQMinChanges = float(
            searchAndGetMatch(
                qssStats,
                f"Variable {varName}:[\S\s]+dQMin changes: (.+)",
            )
        )
        maxError = float(
            searchAndGetMatch(qssStats, f"Variable {varName}:[\S\s]+Max error: (.+)")
        )
        return (dQRelChanges, dQMinChanges, maxError)

    def parse(self, chunks):
        qssStats = chunks["qssStats"]
        varX_dQRelChanges, varX_dQMinChanges, varX_maxError = self.getVariableNStuff(
            "x", qssStats
        )
        varY_dQRelChanges, varY_dQMinChanges, varY_maxError = self.getVariableNStuff(
            "y", qssStats
        )
        varZ_dQRelChanges, varZ_dQMinChanges, varZ_maxError = self.getVariableNStuff(
            "z", qssStats
        )
        varVX_dQRelChanges, varVX_dQMinChanges, varVX_maxError = self.getVariableNStuff(
            "vx", qssStats
        )
        varVY_dQRelChanges, varVY_dQMinChanges, varVY_maxError = self.getVariableNStuff(
            "vy", qssStats
        )
        varVZ_dQRelChanges, varVZ_dQMinChanges, varVZ_maxError = self.getVariableNStuff(
            "vz", qssStats
        )
        return {
            "varX_dQRelChanges": varX_dQRelChanges,
            "varX_dQMinChanges": varX_dQMinChanges,
            "varX_maxError": varX_maxError,
            "varY_dQRelChanges": varY_dQRelChanges,
            "varY_dQMinChanges": varY_dQMinChanges,
            "varY_maxError": varY_maxError,
            "varZ_dQRelChanges": varZ_dQRelChanges,
            "varZ_dQMinChanges": varZ_dQMinChanges,
            "varZ_maxError": varZ_maxError,
            "varVX_dQRelChanges": varVX_dQRelChanges,
            "varVX_dQMinChanges": varVX_dQMinChanges,
            "varVX_maxError": varVX_maxError,
            "varVY_dQRelChanges": varVY_dQRelChanges,
            "varVY_dQMinChanges": varVY_dQMinChanges,
            "varVY_maxError": varVY_maxError,
            "varVZ_dQRelChanges": varVZ_dQRelChanges,
            "varVZ_dQMinChanges": varVZ_dQMinChanges,
            "varVZ_maxError": varVZ_maxError,
        }

    def addAggregatedVarData(self, aggregatedResults, varName, results):
        aggregatedResults[f"var{varName}_dQRelChanges"] = statsOfKeyInArray(
            f"var{varName}_dQRelChanges", results, "changes"
        )
        aggregatedResults[f"var{varName}_dQMinChanges"] = statsOfKeyInArray(
            f"var{varName}_dQMinChanges", results, "changes"
        )
        aggregatedResults[f"var{varName}_maxError"] = statsOfKeyInArray(
            f"var{varName}_maxError", results, "mm?"
        )

    def aggregateRunResults(self, results):

        aggregatedResults = {}

        self.addAggregatedVarData(aggregatedResults, "X", results)
        self.addAggregatedVarData(aggregatedResults, "Y", results)
        self.addAggregatedVarData(aggregatedResults, "Z", results)
        self.addAggregatedVarData(aggregatedResults, "VX", results)
        self.addAggregatedVarData(aggregatedResults, "VY", results)
        self.addAggregatedVarData(aggregatedResults, "VZ", results)

        return aggregatedResults

    def plot(self, graficador, aggregatedResults):
        pass
