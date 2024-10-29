from parsers.utils import searchAndGetMatch
from utils.functions import statsOfKeyInArray


class RunParams:
    def parse(self, chunks):
        qssStats = chunks["qssStats"]
        dQMin = float(searchAndGetMatch(qssStats, "dQMin: (.+)"))
        dQRel = float(searchAndGetMatch(qssStats, "dQRel: (.+)"))
        return {
            "dQMin": dQMin,
            "dQRel": dQRel,
        }

    def aggregateRunResults(self, results):
        aggregatedResults = {}
        aggregatedResults["dQMin"] = statsOfKeyInArray("dQMin", results, "dQMin")
        aggregatedResults["dQRel"] = statsOfKeyInArray("dQRel", results, "dQRel")
        return aggregatedResults

    def plot(self, graficador, aggregatedResults):
        pass
