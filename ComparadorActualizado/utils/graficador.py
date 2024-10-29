from cProfile import label
import matplotlib.pyplot as plt
from config.paths import mkdirIfMissing
import statistics

from utils.functions import onlyNotNone


class Graficador:
    def __init__(self, outputImgsDir):
        self.outputImgsDir = outputImgsDir
        mkdirIfMissing(outputImgsDir)
        self.enabled = True

    def saveAndClose(self, name):
        plt.savefig(
            self.outputImgsDir.joinpath(name + ".png"),
            bbox_inches="tight",
        )
        plt.close()

    def simpleCurvePlot(self, title, xlabel, ylabel, values, xvalues, includeMean):
        if not self.enabled:
            return
        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.plot(xvalues, values, "bo--")
        plt.locator_params(axis="x", integer=True, tight=True)
        if includeMean:
            mean = statistics.mean(onlyNotNone(values))
            plt.plot(xvalues, [mean for _ in values], "r--", label="mean")
            plt.legend()
        self.saveAndClose(name="curve_" + title)

    def simpleHistogramPlot(self, title, xlabel, ylabel, values):
        if not self.enabled:
            return

        try:
            plt.title(title)
            plt.xlabel(xlabel)
            plt.ylabel(ylabel)
            plt.hist(onlyNotNone(values))
            plt.locator_params(axis="y", integer=True, tight=True)
            self.saveAndClose(name="hist_" + title)
        except Exception:
            print(f"Graficador - fail: {title}")
