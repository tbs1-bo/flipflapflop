"""
Water simulation for the flipdot display. Wind blows over the water surface,
pushes the water to one side, creates waves and splashes.

The water is simulated with the FLIP method (particles carry the water, a
grid enforces incompressibility) as explained in "Ten Minute Physics" #18:
https://matthias-research.github.io/pages/tenMinutePhysics/

The wind is provided by a ForceSource. By default random gusts are used.
Start with --mouse to blow with the mouse in the simulator window.
"""
import math
import random
import time

import numpy as np


class ForceSource:
    """Source of the wind force. Subclasses return a signed strength in the
    range -1..1 (positive: wind blows to the right, negative: to the left).
    A sensor can be attached by implementing get_force()."""

    def get_force(self, t):
        "Return the wind force at time t (in seconds)."
        return 0.0


class ConstantForce(ForceSource):
    "Constant wind, mainly for testing."

    def __init__(self, force):
        self.force = force

    def get_force(self, t):
        return self.force


class MouseForce(ForceSource):
    """Wind controlled by the mouse in the pygame simulator window. While a
    mouse button is pressed, the wind blows away from the cursor: the
    closer the cursor is to the left or right edge, the stronger the wind."""

    def get_force(self, t):
        import pygame
        surface = pygame.display.get_surface()
        if surface is None or not any(pygame.mouse.get_pressed()):
            return 0.0
        half = surface.get_width() / 2
        x, _y = pygame.mouse.get_pos()
        return max(-1.0, min(1.0, (half - x) / half))


class GustForce(ForceSource):
    """Random gusts: calm phases alternate with gusts of random direction
    and strength that swell and subside smoothly.

    calm: range (min, max) of the duration of calm phases in seconds.
    gust: range (min, max) of the duration of a gust in seconds.
    strength: range (min, max) of the peak strength of a gust (0..1).
        The direction is chosen randomly.
    """

    def __init__(self, calm=(1.0, 4.0), gust=(1.0, 3.0), strength=(0.4, 1.0)):
        self.calm = calm
        self.gust = gust
        self.strength = strength
        self.gust_start = None
        self.gust_end = None
        self.gust_strength = 0.0

    def _schedule(self, t):
        self.gust_start = t + random.uniform(*self.calm)
        self.gust_end = self.gust_start + random.uniform(*self.gust)
        self.gust_strength = random.choice((-1, 1)) * random.uniform(*self.strength)

    def get_force(self, t):
        if self.gust_start is None or t > self.gust_end:
            self._schedule(t)
        if t < self.gust_start:
            return 0.0
        phase = (t - self.gust_start) / (self.gust_end - self.gust_start)
        return self.gust_strength * math.sin(math.pi * phase) ** 2


FLUID, AIR, SOLID = 0, 1, 2


class WaterSim:
    """FLIP water simulation in a closed basin. Particles carry the water,
    a staggered grid with one cell per display pixel makes the water
    incompressible. All lengths are measured in cells (pixels), time in
    seconds. y points upwards in the simulation.

    Arguments:

    fdd: the display to draw on.
    force_source: ForceSource providing the wind (default: GustForce).
    fps: frame rate of the display. The speed of the simulation does not
        depend on it.

    Water and motion:

    FILL_LEVEL: initial water level relative to the display height.
    GRAVITY: gravity in pixels/s². Sets the pace of the whole simulation:
        higher means fast, restless sloshing, lower means slow motion.
        Keep it rather low for the slow mechanics of flipdots.
    FLIP_RATIO: blend of two methods. 0: pure PIC, viscous like honey,
        waves die out quickly. 1: pure FLIP, very lively but the water
        jitters. 0.9 is the value used in Ten Minute Physics.

    Wind:

    WIND_ACCEL: acceleration of the surface particles at full wind
        (force ±1). Close to GRAVITY gives strong splashes, much lower
        only waves.
    WIND_WAVE_LENGTH: distance in pixels between the spots where the wind
        blows stronger. The uneven wind creates waves: smaller values give
        short choppy waves, larger values a long swell.

    Numerics (accuracy versus computing time):

    PARTICLE_RADIUS: particle radius in cells, determines the number of
        particles. Smaller gives more particles, a denser water body and
        more computing time. Larger gives fewer particles and more holes.
    PRESSURE_ITERS: iterations of the pressure solver per step, which keeps
        the water incompressible. Fewer is faster (first thing to reduce
        on a Raspberry Pi) but the water gets a bit mushy.
    OVER_RELAXATION: speeds up the pressure solver. Valid range 1..2;
        below 1.5 it converges slowly, 2 and above it becomes unstable.
    PUSH_ITERS: how often per step overlapping particles are pushed apart.
        More gives an even distribution and less flickering in the water.
    MAX_PER_CELL: maximum number of particles per cell considered when
        searching neighbours. A technical limit for the numpy arrays,
        usually left unchanged.
    SUBSTEP: length of one simulation step (4 steps per frame at 10 fps).
        Smaller is more stable in strong wind but costs computing time.
        Larger is faster but particles may tunnel through the water.

    Tuning hints: for calmer motion lower GRAVITY and WIND_ACCEL together,
    for more splashes raise WIND_ACCEL. If the Raspberry Pi is too slow,
    first lower PRESSURE_ITERS to 15-20, then raise SUBSTEP to 1/30.
    """

    FILL_LEVEL = 0.4
    GRAVITY = 40.0
    WIND_ACCEL = 30.0
    WIND_WAVE_LENGTH = 10.0
    PARTICLE_RADIUS = 0.3
    FLIP_RATIO = 0.9
    PRESSURE_ITERS = 30
    OVER_RELAXATION = 1.9
    PUSH_ITERS = 2
    MAX_PER_CELL = 8
    SUBSTEP = 1 / 40

    def __init__(self, fdd, force_source=None, fps=10):
        self.fdd = fdd
        self.force_source = force_source or GustForce()
        self.fps = fps
        self.width = fdd.width
        self.height = fdd.height
        # grid with a solid border of one cell around the display area
        self.nx = self.width + 2
        self.ny = self.height + 2
        self.reset()

    def reset(self):
        r = self.PARTICLE_RADIUS
        nx, ny = self.nx, self.ny
        # particles on a hexagonal grid at the bottom of the basin
        dx = 2 * r
        dy = math.sqrt(3) / 2 * dx
        top = 1 + self.height * self.FILL_LEVEL
        pos = []
        y, row = 1 + r, 0
        while y <= top - r:
            x = 1 + r + (r if row % 2 else 0)
            while x <= nx - 1 - r:
                pos.append((x, y))
                x += dx
            y += dy
            row += 1
        self.pos = np.array(pos, dtype=float)
        self.vel = np.zeros_like(self.pos)

        self.s = np.ones((nx, ny))  # 0 for solid cells, 1 otherwise
        self.s[0, :] = self.s[-1, :] = self.s[:, 0] = self.s[:, -1] = 0
        self.u = np.zeros((nx, ny))  # velocity at the left face of a cell
        self.v = np.zeros((nx, ny))  # velocity at the bottom face of a cell
        self.prev_u = np.zeros((nx, ny))
        self.prev_v = np.zeros((nx, ny))
        self.density = np.zeros((nx, ny))
        self.rest_density = 0.0
        i, j = np.indices((nx, ny))
        self.parity = (i + j) % 2
        self.t = 0.0
        self._update_cell_types()

    def step(self, dt, force):
        "Advance the simulation by dt seconds with the given wind force."
        self.t += dt
        self._integrate(dt, force)
        self._push_apart()
        self._collide()
        self._update_cell_types()
        self._to_grid()
        self._update_density()
        self._solve_incompressibility()
        self._to_particles()

    def _cells(self):
        "Index of the cell each particle is in."
        i = np.clip(self.pos[:, 0].astype(int), 0, self.nx - 1)
        j = np.clip(self.pos[:, 1].astype(int), 0, self.ny - 1)
        return i, j

    def _integrate(self, dt, force):
        self.vel[:, 1] -= self.GRAVITY * dt
        if force:
            # the wind only acts on particles with air above them
            i, j = self._cells()
            surface = self.cell_type[i, np.minimum(j + 1, self.ny - 1)] == AIR
            k = 2 * math.pi / self.WIND_WAVE_LENGTH
            x, t = self.pos[:, 0], self.t
            gusty = 1 + 0.3 * np.sin(k * x - 2 * k * force * t) \
                + 0.3 * np.sin(0.37 * k * x - 1.3 * k * force * t + 1)
            self.vel[:, 0] += surface * force * self.WIND_ACCEL * gusty * dt
        self.pos += self.vel * dt

    def _push_apart(self):
        "Separate overlapping particles using a spatial hash."
        n = len(self.pos)
        min_dist = 2 * self.PARTICLE_RADIUS
        size = 2.2 * self.PARTICLE_RADIUS
        hx = int(self.nx / size) + 1
        hy = int(self.ny / size) + 1
        k = self.MAX_PER_CELL
        for _ in range(self.PUSH_ITERS):
            cx = np.clip((self.pos[:, 0] / size).astype(int), 0, hx - 1)
            cy = np.clip((self.pos[:, 1] / size).astype(int), 0, hy - 1)
            cell = cx * hy + cy
            # table with up to k particle indices per hash cell
            order = np.argsort(cell, kind='stable')
            sorted_cell = cell[order]
            start = np.searchsorted(sorted_cell, np.arange(hx * hy))
            rank = np.arange(n) - start[sorted_cell]
            keep = rank < k
            table = np.full((hx * hy, k), -1)
            table[sorted_cell[keep], rank[keep]] = order[keep]

            candidates = []
            for ox in (-1, 0, 1):
                for oy in (-1, 0, 1):
                    ncx, ncy = cx + ox, cy + oy
                    inside = (ncx >= 0) & (ncx < hx) & (ncy >= 0) & (ncy < hy)
                    c = table[np.where(inside, ncx * hy + ncy, 0)]
                    c[~inside] = -1
                    candidates.append(c)
            others = np.concatenate(candidates, axis=1)
            valid = (others >= 0) & (others != np.arange(n)[:, None])
            d = self.pos[:, None, :] - self.pos[np.where(valid, others, 0)]
            dist = np.hypot(d[..., 0], d[..., 1])
            valid &= (dist > 0) & (dist < min_dist)
            # every pair is visited from both sides, each particle moves half
            scale = np.where(valid, 0.5 * (min_dist - dist) / np.where(valid, dist, 1), 0)
            self.pos += (scale[..., None] * d).sum(axis=1)

    def _collide(self):
        r = self.PARTICLE_RADIUS
        for axis, n in ((0, self.nx), (1, self.ny)):
            low = self.pos[:, axis] < 1 + r
            high = self.pos[:, axis] > n - 1 - r
            self.pos[low, axis] = 1 + r
            self.pos[high, axis] = n - 1 - r
            self.vel[low | high, axis] = 0

    def _update_cell_types(self):
        self.cell_type = np.where(self.s == 0, SOLID, AIR)
        i, j = self._cells()
        filled = self.cell_type[i, j] == AIR
        self.cell_type[i[filled], j[filled]] = FLUID

    def _corners(self, ox, oy):
        """Bilinear interpolation of particle positions on a grid shifted by
        (ox, oy). Returns cell indices and weights of the four corners."""
        x = np.clip(self.pos[:, 0], 1, self.nx - 1) - ox
        y = np.clip(self.pos[:, 1], 1, self.ny - 1) - oy
        x0 = np.clip(np.floor(x).astype(int), 0, self.nx - 2)
        y0 = np.clip(np.floor(y).astype(int), 0, self.ny - 2)
        tx, ty = x - x0, y - y0
        return [(x0, y0, (1 - tx) * (1 - ty)), (x0 + 1, y0, tx * (1 - ty)),
                (x0 + 1, y0 + 1, tx * ty), (x0, y0 + 1, (1 - tx) * ty)]

    # (field name, shift of the faces, velocity component, neighbour cell)
    COMPONENTS = (('u', (0.0, 0.5), 0, (-1, 0)), ('v', (0.5, 0.0), 1, (0, -1)))

    def _to_grid(self):
        for name, (ox, oy), axis, (di, dj) in self.COMPONENTS:
            f = np.zeros((self.nx, self.ny))
            w = np.zeros((self.nx, self.ny))
            for i, j, wc in self._corners(ox, oy):
                np.add.at(f, (i, j), wc * self.vel[:, axis])
                np.add.at(w, (i, j), wc)
            f = np.divide(f, w, out=np.zeros_like(f), where=w > 0)
            # faces next to solid cells do not move
            solid = self.s == 0
            solid |= np.roll(solid, (-di, -dj), axis=(0, 1))
            f[solid] = 0
            setattr(self, name, f)
            setattr(self, 'prev_' + name, f.copy())

    def _update_density(self):
        d = np.zeros((self.nx, self.ny))
        for i, j, wc in self._corners(0.5, 0.5):
            np.add.at(d, (i, j), wc)
        self.density = d
        if self.rest_density == 0:
            fluid = self.cell_type == FLUID
            if fluid.any():
                self.rest_density = d[fluid].mean()

    def _solve_incompressibility(self):
        """Gauss-Seidel with red-black ordering: cells of one colour share
        no faces and can be updated at once."""
        u, v, s = self.u, self.v, self.s
        sx0, sx1 = s[:-2, 1:-1], s[2:, 1:-1]
        sy0, sy1 = s[1:-1, :-2], s[1:-1, 2:]
        s_sum = sx0 + sx1 + sy0 + sy1
        fluid = (self.cell_type[1:-1, 1:-1] == FLUID) & (s_sum > 0)
        # push particles out of compressed regions (drift compensation)
        compression = np.maximum(self.density[1:-1, 1:-1] - self.rest_density, 0)
        colours = [fluid & (self.parity[1:-1, 1:-1] == c) for c in (0, 1)]
        s_sum = np.where(s_sum > 0, s_sum, 1)
        for _ in range(self.PRESSURE_ITERS):
            for mask in colours:
                div = u[2:, 1:-1] - u[1:-1, 1:-1] + v[1:-1, 2:] - v[1:-1, 1:-1]
                div -= compression
                p = np.where(mask, -div / s_sum * self.OVER_RELAXATION, 0)
                u[1:-1, 1:-1] -= sx0 * p
                u[2:, 1:-1] += sx1 * p
                v[1:-1, 1:-1] -= sy0 * p
                v[1:-1, 2:] += sy1 * p

    def _to_particles(self):
        for name, (ox, oy), axis, (di, dj) in self.COMPONENTS:
            f = getattr(self, name)
            delta = f - getattr(self, 'prev_' + name)
            # only faces next to water carry a meaningful velocity
            wet = self.cell_type != AIR
            valid = wet | np.roll(wet, (-di, -dj), axis=(0, 1))
            total = pic = flip = 0
            for i, j, wc in self._corners(ox, oy):
                wc = wc * valid[i, j]
                total = total + wc
                pic = pic + wc * f[i, j]
                flip = flip + wc * delta[i, j]
            has = total > 0
            total = np.where(has, total, 1)
            pic = pic / total
            flip = self.vel[:, axis] + flip / total
            mixed = (1 - self.FLIP_RATIO) * pic + self.FLIP_RATIO * flip
            self.vel[:, axis] = np.where(has, mixed, self.vel[:, axis])

    def pixels(self):
        "Boolean array (height x width) with the pixels showing water."
        counts = np.zeros((self.nx, self.ny), dtype=int)
        np.add.at(counts, self._cells(), 1)
        # flip y: display row 0 is the top cell row
        return counts[1:-1, self.ny - 2:0:-1].T > 0

    def draw(self):
        pixels = self.pixels()
        for y in range(self.height):
            for x in range(self.width):
                self.fdd.px(x, y, bool(pixels[y, x]))
        self.fdd.show()

    def one_cycle(self):
        "Simulate and draw one frame."
        force = self.force_source.get_force(time.time())
        steps = max(1, round(1 / self.fps / self.SUBSTEP))
        for _ in range(steps):
            self.step(1 / self.fps / steps, force)
        self.draw()

    def run(self, runtime=None):
        'Run the simulation in an endless loop or for a given time (in seconds)'
        start_time = time.time()
        while (runtime is None) or (time.time() - start_time) < runtime:
            frame_start = time.time()
            self.one_cycle()
            delay = 1 / self.fps - (time.time() - frame_start)
            if delay > 0:
                time.sleep(delay)


def test_particles_stay_inside():
    import displayprovider
    sim = WaterSim(displayprovider.DisplayBase(28, 13))
    count = len(sim.pos)
    for _ in range(200):
        sim.step(sim.SUBSTEP, 1.0)
    assert len(sim.pos) == count
    assert np.isfinite(sim.pos).all()
    assert (sim.pos >= 1).all()
    assert (sim.pos[:, 0] <= sim.nx - 1).all()
    assert (sim.pos[:, 1] <= sim.ny - 1).all()


def test_wind_pushes_water():
    import displayprovider
    sim = WaterSim(displayprovider.DisplayBase(28, 13))
    for _ in range(80):
        sim.step(sim.SUBSTEP, 1.0)
    assert sim.pos[:, 0].mean() > sim.nx / 2


def test_water_settles():
    "Without wind the water keeps its volume and stays at the bottom."
    import displayprovider
    sim = WaterSim(displayprovider.DisplayBase(28, 13))
    before = sim.pixels().sum()
    for _ in range(80):
        sim.step(sim.SUBSTEP, 0.0)
    after = sim.pixels()
    assert abs(after.sum() - before) <= 0.15 * before
    assert not after[0].any()


def test_mouse_force_without_window():
    assert MouseForce().get_force(0) == 0.0


def test_watersim():
    import flipdotsim
    for w, h in ((28, 13), (126, 16)):
        fdd = flipdotsim.FlipDotSim(w, h)
        WaterSim(fdd, ConstantForce(1.0)).run(runtime=1)
        WaterSim(fdd).run(runtime=1)
        fdd.close()


def main():
    import sys
    import displayprovider
    fdd = displayprovider.get_display()
    force_source = None
    if "--mouse" in sys.argv:
        force_source = MouseForce()
        print("Mouse control: hold a mouse button in the simulator window.")
        print("The wind blows away from the cursor, stronger near the edges.")
    else:
        print("Random gusts. Start with --mouse to blow with the mouse.")
    WaterSim(fdd, force_source).run()


if __name__ == "__main__":
    main()
