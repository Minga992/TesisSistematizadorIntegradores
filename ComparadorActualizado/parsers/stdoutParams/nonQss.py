from parsers.utils import searchAndGetMatch
from utils.functions import statsOfKeyInArray


class NonQSS:
    def parse(self, chunks):
        epilogue = chunks["epilogue"]
        userTime = float(
            searchAndGetMatch(epilogue, "RunManager User time:\s*([\d|\.]+)")
        )
        realTime = float(
            searchAndGetMatch(epilogue, "RunManager Real time:\s*([\d|\.]+)")
        )
        systemTime = float(
            searchAndGetMatch(epilogue, "RunManager System time:\s*([\d|\.]+)")
        )

        # Single threading builds produce no ThreadPool output
        numberOfThreads = int(
            searchAndGetMatch(epilogue, "ThreadPool threads: (\d+)", ifAbsent=1)
        )

        intersections = int(
            searchAndGetMatch(epilogue, "G4PropagatorInField - intersections: (\d+)")
        )

        totalSteps = int(searchAndGetMatch(epilogue, "Total steps: (.+)", ifAbsent=0))

        return {
            "userTime": userTime,
            "realTime": realTime,
            "systemTime": systemTime,
            "numberOfThreads": numberOfThreads,
            "intersections": intersections,
            "totalSteps": totalSteps,
        }

    def aggregateRunResults(self, results):
        aggregatedResults = {}
        aggregatedResults["userTime"] = statsOfKeyInArray(
            "userTime", results, "seconds"
        )
        aggregatedResults["realTime"] = statsOfKeyInArray(
            "realTime", results, "seconds"
        )
        aggregatedResults["systemTime"] = statsOfKeyInArray(
            "systemTime", results, "seconds"
        )
        aggregatedResults["numberOfThreads"] = statsOfKeyInArray(
            "numberOfThreads", results, "threads"
        )
        aggregatedResults["intersections"] = statsOfKeyInArray(
            "intersections", results, "intersections"
        )
        aggregatedResults["totalSteps"] = statsOfKeyInArray(
            "totalSteps", results, "steps"
        )
        return aggregatedResults

    def plot(self, graficador, aggregatedResults):
        pass
