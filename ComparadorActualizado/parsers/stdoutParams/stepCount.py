from parsers.utils import searchAndGetAllMatches, searchAndGetMatch
from utils.functions import statsOfKeyInArray, statsOfValues
from parsingConfig import parsingConfig


class StepCount:
    def parse(self, chunks):
        qssStats = chunks["qssStats"]
        totalSteps = int(searchAndGetMatch(qssStats, "Total steps: (.+)"))
        totalSubsteps = int(searchAndGetMatch(qssStats, "Total substeps: (.+)"))
        substepAveragePerStep = float(
            searchAndGetMatch(qssStats, "Substeps average per step: (.+)")
        )
        tracksSubstepInfoString = searchAndGetMatch(
            qssStats, "Substeps by track-step:([\s\S]+)Integration time"
        )
        tracksStepInfo = searchAndGetAllMatches(
            tracksSubstepInfoString, "(Track #(?s).+?)(?=Track #|Integration time)"
        )
        trackData = {}
        for trackStepInfo in tracksStepInfo:
            trackId = searchAndGetMatch(trackStepInfo, "Track #(\d+)")
            stepInfo = searchAndGetAllMatches(
                trackStepInfo, "Step (\d+) => (\d+) substeps"
            )
            stepCount = len(stepInfo)
            substepCount = sum(
                [int(stepSubstepCount) for (_, stepSubstepCount) in stepInfo]
            )
            trackData[trackId] = {
                "stepCount": int(stepCount),
                "substepCount": int(substepCount),
            }

        return {
            "trackData": trackData,
            "numberOfTracks": len(trackData),
            "totalSteps": totalSteps,
            "totalSubsteps": totalSubsteps,
            "substepAveragePerStep": substepAveragePerStep,
        }

    def aggregateRunResults(self, results):
        aggregatedResults = {}
        aggregatedResults["numberOfTracks"] = statsOfKeyInArray(
            "numberOfTracks", results, "tracks"
        )
        aggregatedResults["totalSteps"] = statsOfKeyInArray(
            "totalSteps", results, "steps"
        )
        aggregatedResults["totalSubsteps"] = statsOfKeyInArray(
            "totalSubsteps", results, "substeps"
        )
        aggregatedResults["substepAveragePerStep"] = statsOfKeyInArray(
            "substepAveragePerStep", results, "substeps"
        )
        if parsingConfig.perTrackStats:
            trackAggregatedData = {}
            for experimentTrackData in [result["trackData"] for result in results]:
                for trackId, trackData in experimentTrackData.items():
                    if trackId not in trackAggregatedData:
                        trackAggregatedData[trackId] = {
                            "stepCount": [],
                            "substepCount": [],
                        }
                    trackAggregatedData[trackId]["stepCount"].append(
                        trackData["stepCount"]
                    )
                    trackAggregatedData[trackId]["substepCount"].append(
                        trackData["substepCount"]
                    )

            for trackId, trackData in trackAggregatedData.items():
                aggregatedResults[f"track_{trackId}_stepCount"] = statsOfValues(
                    trackData["stepCount"], "steps"
                )
                aggregatedResults[f"track_{trackId}_substepCount"] = statsOfValues(
                    trackData["substepCount"], "substeps"
                )

        return aggregatedResults

    def plot(self, graficador, aggregatedResults):
        pass
