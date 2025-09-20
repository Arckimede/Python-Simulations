import matplotlib.pyplot as plt
import numpy as np
import scipy 
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Button
from matplotlib.patches import Circle
import random
import warnings

# Suppress the UserWarning from FuncAnimation about blitting with artists
warnings.filterwarnings("ignore", category=UserWarning)


class Molecule:
    def __init__(self, name, x, y, radius, color, ax):
        self.name = name
        self.circle = Circle((x, y), radius, color=color, zorder=2)
        ax.add_artist(self.circle)
        # random velocity
        self.v = np.random.uniform(-0.05, 0.05, 2)
    
    def getCenter(self):
        return np.array(self.circle.center)
    
    def setCenter(self, newCenter):
        self.circle.center = newCenter

    @staticmethod
    def getDistance(moleculeOne, moleculeTwo):
        return scipy.linalg.norm(moleculeOne.getCenter() - moleculeTwo.getCenter())
    
    @staticmethod
    def isColliding(moleculeOne, moleculeTwo):
        dist = Molecule.getDistance(moleculeOne, moleculeTwo)
        sumRadii = moleculeOne.circle.radius + moleculeTwo.circle.radius
        
        if dist <= sumRadii:
            return True
        return False
        
    def move(self, dt, bounds):
        pos = self.getCenter() + self.v * dt

        # x position
        if (pos[0] + self.circle.radius >= bounds[0]):
            pos[0] = bounds[0] - self.circle.radius
            self.v[0] *= -1
        elif (pos[0] - self.circle.radius <= 0):
            pos[0] = self.circle.radius
            self.v[0] *= -1

        # y position
        if (pos[1] + self.circle.radius > bounds[1]):
            pos[1] = bounds[1] - self.circle.radius
            self.v[1] *= -1
        elif (pos[1] - self.circle.radius <= 0):
            pos[1] = self.circle.radius
            self.v[1] *= -1
        
        self.setCenter(pos)
        
    def getClosestNeighbor(self, molecules): 
        closest = None
        minDistance = float("inf")
    
        for other in molecules:
            if other is self:
                continue 
            dist = Molecule.getDistance(self, other)
            if dist < minDistance:
                minDistance = dist
                closest = other
        
        return closest, minDistance

class Simulation:
    def __init__(self, ax, fig):
        self.ax = ax
        self.fig = fig
        self.molecules = []
        self.lines = []
        self.show_connections = True
        self.num_collisions = 0
        self.collision_text = None
        self.avgSpeedText = None
        self.velocityVectors = None

        # Create the buttons and link them to class methods
        ax_show = fig.add_axes([0.3, 0.05, 0.15, 0.05])
        ax_hide = fig.add_axes([0.5, 0.05, 0.15, 0.05])
        self.show_btn = Button(ax_show, "Show Connections", useblit=True, color="#4B52D6", hovercolor="#363EE0")
        self.hide_btn = Button(ax_hide, "Hide Connections", useblit=True, color="#9A9BAD", hovercolor="#8E8F9E")
        self.show_btn.on_clicked(self.toggle_show_connections)
        self.hide_btn.on_clicked(self.toggle_hide_connections)

    def create_molecules(self, nums):
        for _ in range(nums):
            randX = random.randrange(10, 90) / 100
            randY = random.randrange(10, 90) / 100
            randRadius = random.randrange(1, 5) / 100
            
            mol = Molecule("molecule", x=randX, y=randY, radius=randRadius, color="#E5300B", ax=self.ax)
            self.molecules.append(mol)
            
            line, = self.ax.plot([], [], linewidth=1, color="#0B66E5", zorder=1)
            self.lines.append(line)
        
        if self.velocityVectors is None:
            self.velocityVectors = self.ax.quiver(
                np.zeros(nums),
                np.zeros(nums),
                np.zeros(nums),
                np.zeros(nums),
                color="#59E3F8",
                angles="xy",
                scale_units="xy",
                scale=1.0,
                headwidth=5,
                headlength=5,
                zorder=3,
            )     

    def toggle_show_connections(self, event):
        self.show_connections = True

    def toggle_hide_connections(self, event):
        self.show_connections = False
        
    def calcAverageSpeed(self):
        numMolecules = len(self.molecules)
        totalSpeed = 0
        
        if numMolecules == 0:
            return 0.0
        
        for mol in self.molecules:
            speed = np.linalg.norm(mol.v)
            totalSpeed += speed
        return totalSpeed / numMolecules

    def animate(self, frames):
        dt = 1.0
        
        # Movement
        for mol in self.molecules:
            mol.move(dt, bounds=(2, 2))

        # Check for collision
        for i in range(len(self.molecules)):
            for j in range(i + 1, len(self.molecules)):
                if Molecule.isColliding(self.molecules[i], self.molecules[j]):
                    self.num_collisions += 1
        
        # positions and velocities
        xPos = [mol.getCenter()[0] for mol in self.molecules]
        yPos = [mol.getCenter()[1] for mol in self.molecules]
        vxVec = [mol.v[0] for mol in self.molecules]
        vyVec = [mol.v[1] for mol in self.molecules]
        
        self.velocityVectors.set_UVC(vxVec, vyVec)
        self.velocityVectors.set_offsets(list(zip(xPos, yPos)))
        
        # Update text
        if self.collision_text is not None:
            self.collision_text.set_text(f"Collision Count: {int(self.num_collisions)}")

        if self.avgSpeedText is not None:
            self.avgSpeedText.set_text(f"Avg. Molecule Speed: {np.round(self.calcAverageSpeed(), decimals=3)}")

        # Neighbor connections
        artists_to_draw = []
        for i, mol in enumerate(self.molecules):
            neighbor, dist = mol.getClosestNeighbor(self.molecules)
            if neighbor is None or not self.show_connections:
                self.lines[i].set_visible(False)
            else:
                p1 = mol.getCenter()
                p2 = neighbor.getCenter()
                self.lines[i].set_data([p1[0], p2[0]], [p1[1], p2[1]])
                self.lines[i].set_visible(True)

            artists_to_draw.append(mol.circle)
            artists_to_draw.append(self.lines[i])
            artists_to_draw.append(self.velocityVectors)
            
        return tuple(artists_to_draw) + (self.collision_text,)


if __name__ == '__main__':
    # plotting setup
    fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(10, 8))
    fig.subplots_adjust(bottom=0.2)
    ax.set_xlim(0, 2)
    ax.set_ylim(0, 2)
    ax.set_title("Molecules", fontsize=18, color="black")
    
    # Instantiate the simulation class
    sim = Simulation(ax, fig)
    sim.collision_text = ax.text(0.1, 1.85, f"Collision Count: {int(sim.num_collisions)}", fontsize=14)
    sim.avgSpeedText = ax.text(0.1, 1.75, f"Avg. Molecule Speed: {np.round(sim.calcAverageSpeed(), decimals=3)}", fontsize=14)
    sim.create_molecules(nums=10)

    # create and start the animation
    ani = FuncAnimation(
        fig=fig,
        func=sim.animate,
        frames=200,
        interval=20,
        blit=True,
    )
    
    plt.show()