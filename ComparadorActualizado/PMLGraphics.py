import os
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

class QualityExperimentInformation:
    def __init__(
        self, expName, posX, posY, posZ, time, trackLength, posXInterpolated, posYInterpolated, posZInterpolated, commonTime, trackLengthInterpolated
    ):

        self.expName = expName
        self.posX = posX
        self.posY = posY
        self.posZ = posZ
        self.time = time
        self.trackLength = trackLength
        self.posXInterpolated = posXInterpolated
        self.posYInterpolated = posYInterpolated
        self.posZInterpolated = posZInterpolated
        self.commonTime = commonTime
        self.trackLengthInterpolated = trackLengthInterpolated

class PMLGraphics:

    def __init__(
        self, outputDir, qualityExperimentInformation1, qualityExperimentInformation2
    ):
        self.outputDir = outputDir
        self.qualityExperimentInformation1 = qualityExperimentInformation1
        self.qualityExperimentInformation2 = qualityExperimentInformation2
    # self.graphicsName = qualityExperimentInformation1.expName + 'Vs' + qualityExperimentInformation2.expName

    def plot(self):
#print(f"\n> {self.runName}")
        if not os.path.exists(self.outputDir):
            os.makedirs(self.outputDir)

        pmlName1 = self.qualityExperimentInformation1.expName
        pmlName2 = self.qualityExperimentInformation2.expName
        posx1 = self.qualityExperimentInformation1.posX
        posx2 = self.qualityExperimentInformation2.posX
        posy1 = self.qualityExperimentInformation1.posY
        posy2 = self.qualityExperimentInformation2.posY
        posz1 = self.qualityExperimentInformation1.posZ
        posz2 = self.qualityExperimentInformation2.posZ
        t1 = self.qualityExperimentInformation1.time
        t2 = self.qualityExperimentInformation2.time
        trackLength1 = self.qualityExperimentInformation1.trackLength
        trackLength2 = self.qualityExperimentInformation2.trackLength

        posx1_interp = self.qualityExperimentInformation1.posXInterpolated
        posx2_interp = self.qualityExperimentInformation2.posXInterpolated
        posy1_interp = self.qualityExperimentInformation1.posYInterpolated
        posy2_interp = self.qualityExperimentInformation2.posYInterpolated
        posz1_interp = self.qualityExperimentInformation1.posZInterpolated
        posz2_interp = self.qualityExperimentInformation2.posZInterpolated
        t_common = self.qualityExperimentInformation2.commonTime
        trackLength1_interp = self.qualityExperimentInformation1.trackLengthInterpolated
        trackLength2_interp = self.qualityExperimentInformation2.trackLengthInterpolated

        absolutErrorsInX = [abs(x - ref) for x, ref in zip(posx1_interp, posx2_interp)]
        absolutErrorsInY = [abs(x - ref) for x, ref in zip(posy1_interp, posy2_interp)]
        absolutErrorsInZ = [abs(x - ref) for x, ref in zip(posz1_interp, posz2_interp)]

        # Original en x
        plt.figure(figsize=(8, 6))
        plt.scatter(t1, posx1, label=pmlName1 + ' (Original)', color='blue')
        plt.scatter(t2, posx2, label=pmlName2 + ' (Original)', color='red')
        plt.legend()
        plt.xlabel('Time(sec)')
        plt.ylabel('Position(mm)')
        plt.title('Original Data in x')
        plt.savefig(self.outputDir + '/original_dataX.png')
        #plt.show()
        plt.close()

        # Original en y
        plt.figure(figsize=(8, 6))
        plt.scatter(t1, posy1, label=pmlName1 + ' (Original)', color='blue')
        plt.scatter(t2, posy2, label=pmlName2 + ' (Original)', color='red')
        plt.legend()
        plt.xlabel('Time(sec)')
        plt.ylabel('Position(mm)')
        plt.title('Original Data in y')
        plt.savefig(self.outputDir + '/original_dataY.png')
        #plt.show()
        plt.close()

        # Original en z
        plt.figure(figsize=(8, 6))
        plt.scatter(t1, posz1, label=pmlName1 + ' (Original)', color='blue')
        plt.scatter(t2, posz2, label=pmlName2 + ' (Original)', color='red')
        plt.legend()
        plt.xlabel('Time(sec)')
        plt.ylabel('Position(mm)')
        plt.title('Original Data in z')
        plt.savefig(self.outputDir + '/original_dataZ.png')
        #plt.show()
        plt.close()

        # Original en tl
        plt.figure(figsize=(8, 6))
        plt.scatter(t1, trackLength1, label=pmlName1 + ' (Original)', color='blue')
        plt.scatter(t2, trackLength2, label=pmlName2 + ' (Original)', color='red')
        plt.legend()
        plt.xlabel('Time(sec)')
        plt.ylabel('Position(mm)')
        plt.title('Original Data in tl')
        plt.savefig(self.outputDir + '/original_dataTL.png')
        #plt.show()
        plt.close()

        # Interpolado en x

        plt.figure(figsize=(8, 6))
        plt.scatter(t_common, posx1_interp, label=pmlName1 + ' (Interpolado)', color='blue')
        plt.scatter(t_common, posx2_interp, label=pmlName2 + ' (Interpolado)', color='red')
        plt.legend()
        plt.xlabel('Time(sec)')
        plt.ylabel('Position(mm)')
        plt.title('Interpolated Data in x')
        plt.savefig(self.outputDir + '/interpolated_dataX.png')
        #plt.show()
        plt.close()

        # Indice Desempeño en x
        plt.figure(figsize=(8, 6))
        plt.scatter(t_common, absolutErrorsInX, color='blue')
        plt.xlabel('Time(sec)')
        plt.ylabel('Absolut Error(mm)')
        plt.title('Absolut Error in x')
        plt.savefig(self.outputDir + '/absolutError_dataX.png')
        #plt.show()
        plt.close()

        # Interpolado en y

        plt.figure(figsize=(8, 6))
        plt.scatter(t_common, posy1_interp, label=pmlName1 + ' (Interpolado)', color='blue')
        plt.scatter(t_common, posy2_interp, label=pmlName2 + ' (Interpolado)', color='red')
        plt.legend()
        plt.xlabel('Time(sec)')
        plt.ylabel('Position(mm)')
        plt.title('Interpolated Data in y')
        plt.savefig(self.outputDir + '/interpolated_dataY.png')
        #plt.show()
        plt.close()

        # Indice Desempeño en y

        plt.figure(figsize=(8, 6))
        plt.scatter(t_common, absolutErrorsInY, color='blue')
        plt.xlabel('Time(sec)')
        plt.ylabel('Absolut Error(mm)')
        plt.title('Absolut Error in y')
        plt.savefig(self.outputDir + '/absolutError_dataY.png')
        #plt.show()
        plt.close()

        # Interpolado en z

        plt.figure(figsize=(8, 6))
        plt.scatter(t_common, posz1_interp, label=pmlName1 + ' (Interpolado)', color='blue')
        plt.scatter(t_common, posz2_interp, label=pmlName2 + ' (Interpolado)', color='red')
        plt.legend()
        plt.xlabel('Time(sec)')
        plt.ylabel('Position(mm)')
        plt.title('Interpolated Data in z')
        plt.savefig(self.outputDir + '/interpolated_dataZ.png')
        #plt.show()
        plt.close()

        # Indice Desempeño en z

        plt.figure(figsize=(8, 6))
        plt.scatter(t_common, absolutErrorsInZ, color='blue')
        plt.xlabel('Time(sec)')
        plt.ylabel('Absolut Error(mm)')
        plt.title('Absolut Error in z')
        plt.savefig(self.outputDir + '/absolutError_dataZ.png')
        #plt.show()
        plt.close()

        # Interpolado en tl

        plt.figure(figsize=(8, 6))
        plt.scatter(t_common, trackLength1_interp, label=pmlName1 + ' (Interpolado)', color='blue')
        plt.scatter(t_common, trackLength2_interp, label=pmlName2 + ' (Interpolado)', color='red')
        plt.legend()
        plt.xlabel('Time(sec)')
        plt.ylabel('Position(mm)')
        plt.title('Interpolated Data in tl')
        plt.savefig(self.outputDir + '/interpolated_dataTL.png')
        #plt.show()
        plt.close()
        # Graficos 3d

        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        scatter = ax.scatter(posx1, posy1, posz1, c=t1, cmap='viridis', label=pmlName1 + ' (3D)')

        # Agregar la barra de colores
        cbar = plt.colorbar(scatter)
        cbar.set_label('Time(sec)')

        ax.set_xlabel('X(mm)')
        ax.set_ylabel('Y(mm)')
        ax.set_zlabel('Z(mm)')
        ax.set_title('Particle Move of  ' + pmlName1)
        plt.savefig(self.outputDir + '/data3D' + pmlName1 + '.png')
        #plt.show()
        plt.close()

        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        scatter = ax.scatter(posx2, posy2, posz2, c=t2, cmap='viridis', label=pmlName2 + ' (3D)')

        # Agregar la barra de colores
        cbar = plt.colorbar(scatter)
        cbar.set_label('Time(sec)')

        ax.set_xlabel('X(mm)')
        ax.set_ylabel('Y(mm)')
        ax.set_zlabel('Z(mm)')
        ax.set_title('Particle Move of  ' + pmlName2)
        plt.savefig(self.outputDir + '/data3D' + pmlName2 + '.png')
        #plt.show()
        plt.close()