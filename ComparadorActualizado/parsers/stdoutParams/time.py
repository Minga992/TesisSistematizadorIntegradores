from parsers.utils import searchAndGetMatch
from utils.functions import statsOfKeyInArray


class Time:
    def parse(self, chunks):
        qssStats = chunks["qssStats"]
        integrationTime = float(searchAndGetMatch(qssStats, "Integration time: (.+)"))
        integrationTimeAvgStep = float(
            searchAndGetMatch(qssStats, "Integration time average \(step\): (.+)")
        )
        integrationTimeAvgSubstep = float(
            searchAndGetMatch(qssStats, "Integration time average \(substep\): (.+)")
        )
        resetTime = float(searchAndGetMatch(qssStats, "Reset time: (.+)"))
        resetTimeAvg = float(searchAndGetMatch(qssStats, "Reset time average: (.+)"))
        return {
            "integrationTime": integrationTime,
            "integrationTimeAvgStep": integrationTimeAvgStep,
            "integrationTimeAvgSubstep": integrationTimeAvgSubstep,
            "resetTime": resetTime,
            "resetTimeAvg": resetTimeAvg,
        }

    def aggregateRunResults(self, results):
        aggregatedResults = {}
        aggregatedResults["integrationTime"] = statsOfKeyInArray(
            "integrationTime", results, "seconds"
        )
        aggregatedResults["integrationTimeAvgStep"] = statsOfKeyInArray(
            "integrationTimeAvgStep", results, "seconds"
        )
        aggregatedResults["integrationTimeAvgSubstep"] = statsOfKeyInArray(
            "integrationTimeAvgSubstep", results, "seconds"
        )
        aggregatedResults["resetTime"] = statsOfKeyInArray(
            "resetTime", results, "seconds"
        )
        aggregatedResults["resetTimeAvg"] = statsOfKeyInArray(
            "resetTimeAvg", results, "seconds"
        )
        return aggregatedResults

    def plot(self, graficador, aggregatedResults):
        pass
