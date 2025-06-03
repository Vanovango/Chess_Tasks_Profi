import random
import networkx as nx
from svgwrite import Drawing
import subprocess
from tkinter import *
from tkinter import filedialog, messagebox


def generate_grid(size):
    """Generate a grid graph of given size."""
    return nx.grid_2d_graph(size, size)


def place_circles(G, num_circles, cycle):
    """Place circles along the cycle with alternating colors."""
    nodes = list(cycle)
    if num_circles > len(nodes):
        num_circles = len(nodes) // 2  # Ensure feasibility
    circle_indices = random.sample(range(len(nodes)), num_circles)
    circles = [nodes[i] for i in circle_indices]
    colors = {}
    for i, circle in enumerate(circles):
        colors[circle] = 'black' if i % 2 == 0 else 'white'
    return circles, colors


def generate_hamiltonian_cycle(size):
    """Generate a simple Hamiltonian path for an NxN grid using a zigzag pattern."""
    cycle = []
    for i in range(size):
        if i % 2 == 0:
            for j in range(size):
                cycle.append((i, j))
        else:
            for j in range(size - 1, -1, -1):
                cycle.append((i, j))
    return cycle


def check_alternating_colors(cycle, circles, colors):
    """Verify that circle colors alternate along the cycle path."""
    circle_positions = [c for c in cycle if c in circles]
    if not circle_positions:
        return True
    for i in range(len(circle_positions) - 1):
        current = circle_positions[i]
        next_circle = circle_positions[i + 1]
        if colors[current] == colors[next_circle]:
            return False
    return True


def generate_problem(size, num_circles):
    """Generate a rook path problem."""
    G = generate_grid(size)
    cycle = generate_hamiltonian_cycle(size)
    while True:
        circles, colors = place_circles(G, num_circles, cycle)
        if check_alternating_colors(cycle, circles, colors):
            break
    return G, circles, colors, cycle


def save_to_svg(filename, G, circles, colors, size):
    """Save the problem as an SVG file."""
    cell_size = 50
    dwg = Drawing(filename, profile='tiny', size=(size * cell_size, size * cell_size))

    # Draw grid
    for i in range(size + 1):
        dwg.add(dwg.line((0, i * cell_size), (size * cell_size, i * cell_size), stroke='black'))
        dwg.add(dwg.line((i * cell_size, 0), (i * cell_size, size * cell_size), stroke='black'))

    # Draw circles
    for circle in circles:
        x, y = circle
        color = colors[circle]
        dwg.add(dwg.circle(center=((x + 0.5) * cell_size, (y + 0.5) * cell_size),
                           r=cell_size / 4, fill=color, stroke='black'))

    dwg.save()


def convert_svg_to_cdr(svg_filename, cdr_filename):
    """Convert SVG to CDR using Inkscape (must be installed)."""
    subprocess.run(['inkscape', '--export-filename=' + cdr_filename,
                    '--export-type=cdr', svg_filename], check=True)


class RookProblemApp:
    def __init__(self, master):
        self.master = master
        master.title("Rook Problem Generator")

        # Theme
        Label(master, text="Theme:").grid(row=0, column=0, pady=5)
        self.theme_var = StringVar(value="Single Closed Cycle with Alternating Circles")
        OptionMenu(master, self.theme_var, "Single Closed Cycle with Alternating Circles").grid(row=0, column=1)

        # Grid Size
        Label(master, text="Grid Size:").grid(row=1, column=0, pady=5)
        self.grid_size_var = StringVar(value="6x6")
        OptionMenu(master, self.grid_size_var, "6x6", "8x8", "10x10").grid(row=1, column=1)

        # Number of Circles
        Label(master, text="Number of Circles:").grid(row=2, column=0, pady=5)
        self.num_circles_var = IntVar(value=1)
        Spinbox(master, from_=1, to=50, textvariable=self.num_circles_var).grid(row=2, column=1)

        # Buttons
        Button(master, text="Generate Problem", command=self.generate_problem).grid(row=3, column=0, pady=5)
        Button(master, text="Save to CDR", command=self.save_file).grid(row=3, column=1)

        # Status
        self.status_label = Label(master, text="")
        self.status_label.grid(row=4, column=0, columnspan=2, pady=5)

    def generate_problem(self):
        size_str = self.grid_size_var.get()
        size = int(size_str.split('x')[0])
        num_circles = self.num_circles_var.get()
        self.G, self.circles, self.colors, self.cycle = generate_problem(size, num_circles)
        self.size = size
        self.status_label.config(text="Problem generated successfully")

    def save_file(self):
        if not hasattr(self, 'G'):
            self.status_label.config(text="Please generate a problem first")
            return
        filename = filedialog.asksaveasfilename(
            defaultextension=".cdr",
            filetypes=[("CDR files", "*.cdr")],
            title="Save CDR File"
        )
        if filename:
            svg_filename = "temp.svg"
            save_to_svg(svg_filename, self.G, self.circles, self.colors, self.size)
            convert_svg_to_cdr(svg_filename, filename)
            self.status_label.config(text=f"File saved to {filename}")
        else:
            self.status_label.config(text="Save cancelled")


if __name__ == "__main__":
    root = Tk()
    app = RookProblemApp(root)
    root.mainloop()