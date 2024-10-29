import re

from utils.functions import statsOfKeyInArray

aristasInteresantes = [
    "G4PropagatorInField::ComputeStep",
    "AdvanceChordLimited",  # "G4ChordFinder::AdvanceChordLimited",
    # "G4MultiLevelLocator::EstimateIntersectionPoint",
    # "G4PropagatorInField::IntersectChord",
]


class DotfileParser:

    # Mega naive regex parse de los nodo/aristas que nos interesan.
    # Podríamos parsear el perf.data, o los dot con alguna biblioteca, pero esto texto plano es suficiente por ahora
    def parse(self, file):
        with open(file, "r") as f:
            content = f.read()
            output = {}
            for aristaInteresante in aristasInteresantes:
                searchRes = re.search(
                    f'(?:-> ".*{aristaInteresante}.+label=")(\d+\.\d+)',
                    content,
                )
                resArista = float(searchRes.groups()[0])
                output[aristaInteresante] = resArista
            return output

    def aggregateRunResults(self, results):
        aristas = [arista for arista in results[0]]
        aggregatedResults = {}
        for arista in aristas:
            aggregatedResults[arista] = statsOfKeyInArray(
                arista, results, "% inclusive"
            )
        return aggregatedResults
