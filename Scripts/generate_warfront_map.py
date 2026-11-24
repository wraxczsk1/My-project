import array
import json
import math
import os
import random
import struct
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "Content" / "Warfront" / "Maps" / "WarfrontAIMap.glb"
SEED = 5808
MAP_HALF_SIZE = 6000.0
GRID_SIZE = 257

MATERIALS = [
    ("grass", (0.13, 0.20, 0.075, 1.0), 1.0),
    ("asphalt", (0.095, 0.105, 0.105, 1.0), 0.96),
    ("dirt", (0.27, 0.20, 0.12, 1.0), 1.0),
    ("water", (0.035, 0.12, 0.16, 1.0), 0.22),
    ("bark", (0.16, 0.095, 0.052, 1.0), 1.0),
    ("leaves_dark", (0.065, 0.14, 0.045, 1.0), 1.0),
    ("leaves_light", (0.12, 0.22, 0.07, 1.0), 1.0),
    ("concrete", (0.31, 0.30, 0.265, 1.0), 0.94),
    ("roof", (0.17, 0.13, 0.105, 1.0), 0.92),
    ("window", (0.025, 0.045, 0.055, 1.0), 0.6),
    ("metal", (0.085, 0.105, 0.11, 1.0), 0.78),
    ("rock", (0.20, 0.205, 0.19, 1.0), 1.0),
]

TOWNS = (
    (0.0, 0.0, 34),
    (-2850.0, 2450.0, 13),
    (3250.0, 1800.0, 13),
    (-3000.0, -2350.0, 13),
    (2500.0, -3200.0, 13),
)

MOUNTAINS = (
    (-4700.0, -4100.0, 900.0, 1500.0),
    (-4000.0, 4200.0, 720.0, 1700.0),
    (-500.0, 5050.0, 940.0, 1450.0),
    (3900.0, 4250.0, 860.0, 1650.0),
    (4800.0, 600.0, 760.0, 1350.0),
    (4450.0, -4200.0, 1050.0, 1700.0),
    (650.0, -5000.0, 820.0, 1550.0),
    (-4700.0, -800.0, 620.0, 1450.0),
)

ROADS = (
    ((0.0, 0.0), (-500.0, 500.0), (-1500.0, 1550.0), (-2850.0, 2450.0)),
    ((0.0, 0.0), (850.0, 300.0), (2050.0, 1000.0), (3250.0, 1800.0)),
    ((0.0, 0.0), (-500.0, -900.0), (-1700.0, -1750.0), (-3000.0, -2350.0)),
    ((0.0, 0.0), (800.0, -750.0), (1750.0, -2050.0), (2500.0, -3200.0)),
    ((-2850.0, 2450.0), (-500.0, 2750.0), (1350.0, 2600.0), (3250.0, 1800.0)),
)

FORESTS = (
    (-4600.0, 2200.0, 650),
    (-3750.0, -4200.0, 480),
    (-1600.0, 4700.0, 420),
    (4300.0, 3100.0, 520),
    (4700.0, -1550.0, 560),
    (1700.0, -4600.0, 520),
    (-4300.0, -900.0, 400),
    (1200.0, 3900.0, 360),
)


def _dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def _sub(a, b):
    return a[0] - b[0], a[1] - b[1], a[2] - b[2]


def _cross(a, b):
    return (
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    )


def _normalize(value):
    length = math.sqrt(_dot(value, value))
    if length < 1e-8:
        return 0.0, 1.0, 0.0
    return value[0] / length, value[1] / length, value[2] / length


class MeshPart:
    def __init__(self):
        self.positions = []
        self.normals = []
        self.uvs = []
        self.indices = []

    def add_vertex(self, position, normal, uv):
        index = len(self.positions)
        self.positions.append(position)
        self.normals.append(normal)
        self.uvs.append(uv)
        return index

    def add_triangle(self, a, b, c):
        normal = _normalize(_cross(_sub(b, a), _sub(c, a)))
        start = len(self.positions)
        self.positions.extend((a, b, c))
        self.normals.extend((normal, normal, normal))
        self.uvs.extend(((0.0, 0.0), (1.0, 0.0), (1.0, 1.0)))
        self.indices.extend((start, start + 1, start + 2))

    def add_quad(self, a, b, c, d):
        self.add_triangle(a, b, c)
        self.add_triangle(a, c, d)


class MeshBuilder:
    def __init__(self, name):
        self.name = name
        self.parts = {}

    def part(self, material):
        if material not in self.parts:
            self.parts[material] = MeshPart()
        return self.parts[material]


def _height(x, z):
    rolling = (
        145.0
        + 62.0 * math.sin(x / 690.0) * math.cos(z / 830.0)
        + 34.0 * math.sin((x + z) / 390.0)
        + 18.0 * math.cos((x - 1.7 * z) / 240.0)
    )
    mountain = 0.0
    for center_x, center_z, peak, radius in MOUNTAINS:
        dx = (x - center_x) / radius
        dz = (z - center_z) / radius
        mountain += peak * math.exp(-0.5 * (dx * dx + dz * dz))
    ridge = 55.0 * abs(math.sin((x + 0.38 * z) / 970.0))
    valley_axis = 920.0 * math.sin(x / 1850.0) - 850.0
    valley = 105.0 * math.exp(-0.5 * ((z - valley_axis) / 520.0) ** 2)
    height = max(35.0, rolling + mountain + ridge - valley)

    town_weight = 0.0
    for town_x, town_z, _ in TOWNS:
        dx = (x - town_x) / 560.0
        dz = (z - town_z) / 480.0
        town_weight = max(town_weight, math.exp(-0.5 * (dx * dx + dz * dz)))
    return height * (1.0 - 0.82 * town_weight) + 92.0 * town_weight


def _rotate_y(point, yaw):
    x, y, z = point
    cosine = math.cos(yaw)
    sine = math.sin(yaw)
    return x * cosine + z * sine, y, -x * sine + z * cosine


def _world_point(local, center, yaw):
    x, y, z = _rotate_y(local, yaw)
    return center[0] + x, center[1] + y, center[2] + z


def _add_box(builder, material, center, size, yaw=0.0):
    half_x, half_y, half_z = size[0] / 2.0, size[1] / 2.0, size[2] / 2.0
    local = (
        (-half_x, -half_y, -half_z),
        (half_x, -half_y, -half_z),
        (half_x, half_y, -half_z),
        (-half_x, half_y, -half_z),
        (-half_x, -half_y, half_z),
        (half_x, -half_y, half_z),
        (half_x, half_y, half_z),
        (-half_x, half_y, half_z),
    )
    vertices = [_world_point(point, center, yaw) for point in local]
    faces = (
        (0, 3, 2, 1),
        (4, 5, 6, 7),
        (0, 4, 7, 3),
        (1, 2, 6, 5),
        (3, 7, 6, 2),
        (0, 1, 5, 4),
    )
    part = builder.part(material)
    for a, b, c, d in faces:
        part.add_quad(vertices[a], vertices[b], vertices[c], vertices[d])


def _add_cylinder_between(builder, material, start, end, radius, sides=7, end_radius=None):
    axis = _normalize(_sub(end, start))
    helper = (0.0, 0.0, 1.0) if abs(axis[1]) > 0.9 else (0.0, 1.0, 0.0)
    u = _normalize(_cross(axis, helper))
    v = _normalize(_cross(axis, u))
    top_radius = radius if end_radius is None else end_radius
    rings = []
    for point, ring_radius in ((start, radius), (end, top_radius)):
        ring = []
        for side in range(sides):
            angle = 2.0 * math.pi * side / sides
            ring.append(
                (
                    point[0] + ring_radius * (u[0] * math.cos(angle) + v[0] * math.sin(angle)),
                    point[1] + ring_radius * (u[1] * math.cos(angle) + v[1] * math.sin(angle)),
                    point[2] + ring_radius * (u[2] * math.cos(angle) + v[2] * math.sin(angle)),
                )
            )
        rings.append(ring)
    part = builder.part(material)
    for side in range(sides):
        next_side = (side + 1) % sides
        part.add_quad(
            rings[0][side],
            rings[0][next_side],
            rings[1][next_side],
            rings[1][side],
        )
        part.add_triangle(start, rings[0][next_side], rings[0][side])
        part.add_triangle(end, rings[1][side], rings[1][next_side])


def _add_cone(builder, material, center, radius, height, sides, rotation=0.0):
    bottom = []
    for side in range(sides):
        angle = 2.0 * math.pi * side / sides + rotation
        bottom.append(
            (
                center[0] + radius * math.cos(angle),
                center[1],
                center[2] + radius * math.sin(angle),
            )
        )
    tip = (center[0], center[1] + height, center[2])
    part = builder.part(material)
    base = (center[0], center[1], center[2])
    for side in range(sides):
        next_side = (side + 1) % sides
        part.add_triangle(bottom[side], bottom[next_side], tip)
        part.add_triangle(base, bottom[next_side], bottom[side])


def _add_ellipsoid(builder, material, center, radii, sides=9, rings=5, phase=0.0):
    latitudes = []
    for ring in range(1, rings):
        latitude = -math.pi / 2.0 + math.pi * ring / rings
        row = []
        for side in range(sides):
            longitude = 2.0 * math.pi * side / sides + phase
            row.append(
                (
                    center[0] + radii[0] * math.cos(latitude) * math.cos(longitude),
                    center[1] + radii[1] * math.sin(latitude),
                    center[2] + radii[2] * math.cos(latitude) * math.sin(longitude),
                )
            )
        latitudes.append(row)
    top = (center[0], center[1] + radii[1], center[2])
    bottom = (center[0], center[1] - radii[1], center[2])
    part = builder.part(material)
    for side in range(sides):
        next_side = (side + 1) % sides
        part.add_triangle(top, latitudes[0][side], latitudes[0][next_side])
        part.add_triangle(bottom, latitudes[-1][next_side], latitudes[-1][side])
    for ring in range(len(latitudes) - 1):
        for side in range(sides):
            next_side = (side + 1) % sides
            part.add_quad(
                latitudes[ring][side],
                latitudes[ring + 1][side],
                latitudes[ring + 1][next_side],
                latitudes[ring][next_side],
            )


def _distance_to_segment(x, z, start, end):
    dx = end[0] - start[0]
    dz = end[1] - start[1]
    length_squared = dx * dx + dz * dz
    if length_squared < 1e-6:
        return math.hypot(x - start[0], z - start[1])
    amount = max(
        0.0,
        min(1.0, ((x - start[0]) * dx + (z - start[1]) * dz) / length_squared),
    )
    closest_x = start[0] + amount * dx
    closest_z = start[1] + amount * dz
    return math.hypot(x - closest_x, z - closest_z)


def _road_clearance(x, z):
    distance = MAP_HALF_SIZE
    for road in ROADS:
        for index in range(len(road) - 1):
            distance = min(
                distance,
                _distance_to_segment(x, z, road[index], road[index + 1]),
            )
    return distance


def _make_terrain():
    builder = MeshBuilder("Terrain")
    part = builder.part("grass")
    step = (MAP_HALF_SIZE * 2.0) / (GRID_SIZE - 1)
    for row in range(GRID_SIZE):
        z = -MAP_HALF_SIZE + row * step
        for column in range(GRID_SIZE):
            x = -MAP_HALF_SIZE + column * step
            y = _height(x, z)
            delta = 8.0
            dx = (_height(x + delta, z) - _height(x - delta, z)) / (2.0 * delta)
            dz = (_height(x, z + delta) - _height(x, z - delta)) / (2.0 * delta)
            normal = _normalize((-dx, 1.0, -dz))
            index = part.add_vertex(
                (x, y, z),
                normal,
                (column / 24.0, row / 24.0),
            )
            if column < GRID_SIZE - 1 and row < GRID_SIZE - 1:
                right = index + 1
                down = index + GRID_SIZE
                down_right = down + 1
                part.indices.extend((index, down, right, right, down, down_right))
    return builder


def _make_roads():
    builder = MeshBuilder("Roads")
    for road_index, road in enumerate(ROADS):
        width = 25.0 if road_index < 4 else 16.0
        material = "asphalt" if road_index < 4 else "dirt"
        part = builder.part(material)
        for segment in range(len(road) - 1):
            start = road[segment]
            end = road[segment + 1]
            dx = end[0] - start[0]
            dz = end[1] - start[1]
            length = math.hypot(dx, dz)
            if length < 1.0:
                continue
            side_x = -dz / length * width / 2.0
            side_z = dx / length * width / 2.0
            a = (start[0] + side_x, _height(start[0] + side_x, start[1] + side_z) + 0.08, start[1] + side_z)
            b = (start[0] - side_x, _height(start[0] - side_x, start[1] - side_z) + 0.08, start[1] - side_z)
            c = (end[0] - side_x, _height(end[0] - side_x, end[1] - side_z) + 0.08, end[1] - side_z)
            d = (end[0] + side_x, _height(end[0] + side_x, end[1] + side_z) + 0.08, end[1] + side_z)
            part.add_quad(b, a, d, c)
            shoulder = builder.part("dirt")
            outer_x = side_x * 1.4
            outer_z = side_z * 1.4
            shoulder.add_quad(
                (start[0] + side_x, _height(start[0] + side_x, start[1] + side_z) + 0.04, start[1] + side_z),
                (start[0] + outer_x, _height(start[0] + outer_x, start[1] + outer_z) + 0.04, start[1] + outer_z),
                (end[0] + outer_x, _height(end[0] + outer_x, end[1] + outer_z) + 0.04, end[1] + outer_z),
                (end[0] + side_x, _height(end[0] + side_x, end[1] + side_z) + 0.04, end[1] + side_z),
            )
            shoulder.add_quad(
                (start[0] - outer_x, _height(start[0] - outer_x, start[1] - outer_z) + 0.04, start[1] - outer_z),
                (start[0] - side_x, _height(start[0] - side_x, start[1] - side_z) + 0.04, start[1] - side_z),
                (end[0] - side_x, _height(end[0] - side_x, end[1] - side_z) + 0.04, end[1] - side_z),
                (end[0] - outer_x, _height(end[0] - outer_x, end[1] - outer_z) + 0.04, end[1] - outer_z),
            )
    return builder


def _make_tree(builder, rng, x, z):
    ground = _height(x, z)
    yaw = rng.random() * math.tau
    trunk_height = rng.uniform(10.0, 17.0)
    trunk_radius = rng.uniform(0.45, 0.9)
    base = (x, ground, z)
    top = (x + math.sin(yaw) * 0.8, ground + trunk_height, z + math.cos(yaw) * 0.8)
    _add_cylinder_between(builder, "bark", base, top, trunk_radius, sides=7, end_radius=trunk_radius * 0.5)

    branch_count = rng.randint(2, 4)
    for branch in range(branch_count):
        angle = yaw + branch * math.tau / branch_count + rng.uniform(-0.25, 0.25)
        branch_start_y = ground + trunk_height * rng.uniform(0.4, 0.7)
        branch_length = rng.uniform(3.0, 5.2)
        branch_end = (
            x + math.cos(angle) * branch_length,
            branch_start_y + rng.uniform(1.5, 3.2),
            z + math.sin(angle) * branch_length,
        )
        _add_cylinder_between(
            builder,
            "bark",
            (x, branch_start_y, z),
            branch_end,
            trunk_radius * 0.42,
            sides=5,
            end_radius=trunk_radius * 0.18,
        )

    if rng.random() < 0.34:
        crown_center = (x, ground + trunk_height * 0.78, z)
        radius = rng.uniform(4.0, 6.0)
        _add_ellipsoid(
            builder,
            "leaves_light",
            crown_center,
            (radius, radius * rng.uniform(0.9, 1.3), radius),
            sides=8,
            rings=5,
            phase=yaw,
        )
        return

    layers = rng.randint(3, 4)
    for layer in range(layers):
        fraction = layer / layers
        radius = trunk_height * (0.36 - fraction * 0.21) * rng.uniform(0.82, 1.08)
        center = (
            top[0],
            ground + trunk_height * (0.42 + fraction * 0.17),
            top[2],
        )
        material = "leaves_dark" if layer % 2 == 0 else "leaves_light"
        _add_cone(
            builder,
            material,
            center,
            radius,
            trunk_height * (0.48 - fraction * 0.08),
            sides=8,
            rotation=yaw + layer * 0.19,
        )


def _make_vegetation():
    builder = MeshBuilder("Vegetation")
    rng = random.Random(SEED + 2)
    for center_x, center_z, count in FORESTS:
        created = 0
        attempts = 0
        while created < count and attempts < count * 5:
            attempts += 1
            angle = rng.random() * math.tau
            radius = math.sqrt(rng.random()) * rng.uniform(380.0, 1250.0)
            x = center_x + math.cos(angle) * radius
            z = center_z + math.sin(angle) * radius
            if abs(x) > MAP_HALF_SIZE - 120.0 or abs(z) > MAP_HALF_SIZE - 120.0:
                continue
            if math.hypot(x, z) < 510.0 or _road_clearance(x, z) < 80.0:
                continue
            _make_tree(builder, rng, x, z)
            created += 1
    return builder


def _add_world_quad(builder, material, points, center_x, center_z, yaw):
    center = (center_x, 0.0, center_z)
    rotated = [_world_point(point, center, yaw) for point in points]
    builder.part(material).add_quad(*rotated)


def _make_building(builder, rng, x, z, yaw):
    ground = _height(x, z)
    width = rng.uniform(15.0, 34.0)
    depth = rng.uniform(13.0, 29.0)
    wall_height = rng.uniform(8.0, 14.0)
    wall = 0.9
    center = (x, ground + wall_height / 2.0, z)

    _add_box(builder, "concrete", (x, ground + 0.45, z), (width, 0.9, depth), yaw)
    if rng.random() < 0.22:
        _add_box(
            builder,
            "concrete",
            _world_point((0.0, wall_height * 0.25, -depth / 2.0 + wall / 2.0), (x, ground, z), yaw),
            (width * 0.62, wall_height * 0.5, wall),
            yaw,
        )
    else:
        _add_box(
            builder,
            "concrete",
            _world_point((0.0, center[1] - ground, -depth / 2.0 + wall / 2.0), (x, ground, z), yaw),
            (width, wall_height, wall),
            yaw,
        )
        _add_box(
            builder,
            "concrete",
            _world_point((0.0, center[1] - ground, depth / 2.0 - wall / 2.0), (x, ground, z), yaw),
            (width, wall_height, wall),
            yaw,
        )
    _add_box(
        builder,
        "concrete",
        _world_point((-width / 2.0 + wall / 2.0, wall_height / 2.0, 0.0), (x, ground, z), yaw),
        (wall, wall_height, depth),
        yaw,
    )
    _add_box(
        builder,
        "concrete",
        _world_point((width / 2.0 - wall / 2.0, wall_height / 2.0, 0.0), (x, ground, z), yaw),
        (wall, wall_height, depth),
        yaw,
    )

    roof_y = ground + wall_height
    rise = rng.uniform(3.5, 6.0)
    _add_world_quad(
        builder,
        "roof",
        (
            (-width / 2.0, roof_y, -depth / 2.0),
            (0.0, roof_y + rise, -depth / 2.0),
            (0.0, roof_y + rise, depth / 2.0),
            (-width / 2.0, roof_y, depth / 2.0),
        ),
        x,
        z,
        yaw,
    )
    _add_world_quad(
        builder,
        "roof",
        (
            (0.0, roof_y + rise, -depth / 2.0),
            (width / 2.0, roof_y, -depth / 2.0),
            (width / 2.0, roof_y, depth / 2.0),
            (0.0, roof_y + rise, depth / 2.0),
        ),
        x,
        z,
        yaw,
    )

    front_z = -depth / 2.0 - 0.06
    for side_x in (-width * 0.28, width * 0.28):
        if rng.random() < 0.78:
            _add_box(
                builder,
                "window",
                _world_point((side_x, wall_height * 0.63, front_z), (x, ground, z), yaw),
                (width * 0.15, wall_height * 0.24, 0.16),
                yaw,
            )
    _add_box(
        builder,
        "window",
        _world_point((0.0, wall_height * 0.22, front_z - 0.02), (x, ground, z), yaw),
        (width * 0.16, wall_height * 0.42, 0.18),
        yaw,
    )

    if rng.random() < 0.38:
        for _ in range(rng.randint(3, 7)):
            rubble_x = x + rng.uniform(-width, width)
            rubble_z = z + rng.uniform(-depth, depth)
            rubble_y = _height(rubble_x, rubble_z)
            size = rng.uniform(1.0, 3.2)
            _add_box(
                builder,
                "rock",
                (rubble_x, rubble_y + size / 2.0, rubble_z),
                (size, size * rng.uniform(0.3, 0.9), size * rng.uniform(0.7, 1.4)),
                rng.random() * math.tau,
            )


def _make_buildings():
    builder = MeshBuilder("Buildings")
    rng = random.Random(SEED + 3)
    for town_index, (center_x, center_z, count) in enumerate(TOWNS):
        columns = max(3, int(math.ceil(math.sqrt(count))))
        spacing = 115.0 if town_index == 0 else 95.0
        for index in range(count):
            row, column = divmod(index, columns)
            x = center_x + (column - (columns - 1) / 2.0) * spacing + rng.uniform(-20.0, 20.0)
            z = center_z + (row - (columns - 1) / 2.0) * spacing + rng.uniform(-20.0, 20.0)
            _make_building(builder, rng, x, z, rng.random() * math.tau)

    # A damaged command tower gives the central district a recognizable landmark.
    x, z = 135.0, -85.0
    ground = _height(x, z)
    _add_box(builder, "concrete", (x, ground + 24.0, z), (22.0, 48.0, 22.0))
    _add_box(builder, "concrete", (x, ground + 52.0, z), (30.0, 8.0, 30.0))
    _add_box(builder, "roof", (x, ground + 72.0, z), (23.0, 30.0, 23.0))
    return builder


def _make_vehicle(builder, x, z, yaw, rng):
    ground = _height(x, z)
    center = (x, ground + 1.1, z)
    _add_box(builder, "metal", center, (8.5, 2.2, 3.6), yaw)
    _add_box(
        builder,
        "concrete",
        _world_point((0.1, 1.6, 0.0), center, yaw),
        (3.4, 1.9, 2.8),
        yaw,
    )
    _add_box(
        builder,
        "metal",
        _world_point((0.0, 2.5, 0.0), center, yaw),
        (2.8, 0.8, 2.3),
        yaw,
    )
    barrel_start = _world_point((1.3, 2.55, 0.0), center, yaw)
    barrel_end = _world_point((5.0, 2.3, 0.0), center, yaw)
    _add_cylinder_between(builder, "metal", barrel_start, barrel_end, 0.24, sides=8, end_radius=0.15)
    for side in (-1.0, 1.0):
        for wheel_index in range(4):
            local = (-2.8 + wheel_index * 1.85, -0.45, side * 1.85)
            wheel = _world_point(local, center, yaw)
            _add_cylinder_between(
                builder,
                "rock",
                (wheel[0] - 0.3, wheel[1], wheel[2]),
                (wheel[0] + 0.3, wheel[1], wheel[2]),
                0.62,
                sides=7,
            )
    if rng.random() < 0.65:
        _add_ellipsoid(
            builder,
            "rock",
            (x - 1.0, ground + 5.4, z + 0.4),
            (2.2, 1.4, 1.8),
            sides=7,
            rings=4,
            phase=yaw,
        )


def _make_props():
    builder = MeshBuilder("BattlefieldProps")
    rng = random.Random(SEED + 4)
    vehicle_sites = (
        (-680.0, 220.0),
        (730.0, -340.0),
        (-1180.0, 1180.0),
        (1850.0, 780.0),
        (-2280.0, 1950.0),
        (2850.0, 1450.0),
        (-2550.0, -1880.0),
        (2200.0, -2710.0),
    )
    for x, z in vehicle_sites:
        _make_vehicle(builder, x, z, rng.random() * math.tau, rng)

    for x, z, _ in TOWNS[1:]:
        ground = _height(x, z)
        for index in range(10):
            angle = index * math.tau / 10.0
            px = x + math.cos(angle) * 32.0
            pz = z + math.sin(angle) * 32.0
            py = _height(px, pz)
            _add_box(
                builder,
                "rock",
                (px, py + 1.1, pz),
                (3.4, 2.2, 2.8),
                angle,
            )
        _add_box(builder, "concrete", (x, ground + 4.0, z), (28.0, 8.0, 24.0))
        _add_box(builder, "metal", (x + 12.0, ground + 13.0, z), (2.0, 18.0, 2.0))

        # Field tents and sandbag firing positions at each base.
        for tent_index in range(4):
            tx = x + (-22.0 + tent_index * 15.0)
            tz = z + 42.0
            tent_ground = _height(tx, tz)
            _add_box(builder, "bark", (tx, tent_ground + 4.0, tz), (14.0, 8.0, 22.0), rng.random() * 0.25)
            _add_ellipsoid(
                builder,
                "roof",
                (tx, tent_ground + 9.0, tz),
                (8.0, 5.0, 13.0),
                sides=8,
                rings=4,
            )

        for bunker_index in range(8):
            bx = x + (-44.0 + bunker_index * 12.0)
            bz = z - 48.0
            bunker_ground = _height(bx, bz)
            _add_box(
                builder,
                "concrete",
                (bx, bunker_ground + 1.2, bz),
                (7.0, 2.4, 5.0),
                rng.random() * math.tau,
            )

    # A shallow watercourse crosses the southern valley.
    water = builder.part("water")
    river_points = []
    for step in range(33):
        x = -4300.0 + step * 270.0
        z = -2350.0 + 420.0 * math.sin(x / 1350.0)
        river_points.append((x, z))
    for index in range(len(river_points) - 1):
        start = river_points[index]
        end = river_points[index + 1]
        dx, dz = end[0] - start[0], end[1] - start[1]
        length = max(1.0, math.hypot(dx, dz))
        side_x, side_z = -dz / length * 30.0, dx / length * 30.0
        a = (start[0] + side_x, _height(start[0], start[1]) - 1.0, start[1] + side_z)
        b = (start[0] - side_x, _height(start[0], start[1]) - 1.0, start[1] - side_z)
        c = (end[0] - side_x, _height(end[0], end[1]) - 1.0, end[1] - side_z)
        d = (end[0] + side_x, _height(end[0], end[1]) - 1.0, end[1] + side_z)
        water.add_quad(b, a, d, c)
    return builder


def _pack_floats(values):
    packed = array.array("f")
    for value in values:
        packed.extend(value)
    if sys.byteorder != "little":
        packed.byteswap()
    return packed.tobytes()


def _pack_indices(values):
    packed = array.array("I", values)
    if sys.byteorder != "little":
        packed.byteswap()
    return packed.tobytes()


def _write_glb(builders):
    material_indices = {name: index for index, (name, _, _) in enumerate(MATERIALS)}
    binary = bytearray()
    buffer_views = []
    accessors = []
    gltf_meshes = []

    def add_view(data, target):
        while len(binary) % 4:
            binary.append(0)
        offset = len(binary)
        binary.extend(data)
        view = {"buffer": 0, "byteOffset": offset, "byteLength": len(data)}
        if target is not None:
            view["target"] = target
        buffer_views.append(view)
        return len(buffer_views) - 1

    def add_accessor(view_index, component_type, count, value_type, minimum=None, maximum=None):
        accessor = {
            "bufferView": view_index,
            "componentType": component_type,
            "count": count,
            "type": value_type,
        }
        if minimum is not None:
            accessor["min"] = minimum
        if maximum is not None:
            accessor["max"] = maximum
        accessors.append(accessor)
        return len(accessors) - 1

    for builder in builders:
        primitives = []
        for material_name, part in builder.parts.items():
            if not part.indices:
                continue
            position_min = [
                min(vertex[axis] for vertex in part.positions) for axis in range(3)
            ]
            position_max = [
                max(vertex[axis] for vertex in part.positions) for axis in range(3)
            ]
            position_accessor = add_accessor(
                add_view(_pack_floats(part.positions), 34962),
                5126,
                len(part.positions),
                "VEC3",
                position_min,
                position_max,
            )
            normal_accessor = add_accessor(
                add_view(_pack_floats(part.normals), 34962),
                5126,
                len(part.normals),
                "VEC3",
            )
            uv_accessor = add_accessor(
                add_view(_pack_floats(part.uvs), 34962),
                5126,
                len(part.uvs),
                "VEC2",
            )
            index_accessor = add_accessor(
                add_view(_pack_indices(part.indices), 34963),
                5125,
                len(part.indices),
                "SCALAR",
            )
            primitives.append(
                {
                    "attributes": {
                        "POSITION": position_accessor,
                        "NORMAL": normal_accessor,
                        "TEXCOORD_0": uv_accessor,
                    },
                    "indices": index_accessor,
                    "material": material_indices[material_name],
                    "mode": 4,
                }
            )
        if not primitives:
            raise RuntimeError("Generated mesh has no triangles: " + builder.name)
        gltf_meshes.append({"name": builder.name, "primitives": primitives})

    gltf = {
        "asset": {"version": "2.0", "generator": "Warfront procedural battlefield"},
        "scene": 0,
        "scenes": [{"nodes": list(range(len(gltf_meshes)))}],
        "nodes": [
            {"mesh": index, "name": builder.name}
            for index, builder in enumerate(builders)
        ],
        "meshes": gltf_meshes,
        "materials": [
            {
                "name": name,
                "doubleSided": True,
                "pbrMetallicRoughness": {
                    "baseColorFactor": list(color),
                    "metallicFactor": 0.0,
                    "roughnessFactor": roughness,
                },
            }
            for name, color, roughness in MATERIALS
        ],
        "buffers": [{"byteLength": len(binary)}],
        "bufferViews": buffer_views,
        "accessors": accessors,
    }

    json_chunk = json.dumps(gltf, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    while len(json_chunk) % 4:
        json_chunk += b" "
    while len(binary) % 4:
        binary.append(0)
    total_length = 12 + 8 + len(json_chunk) + 8 + len(binary)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT, "wb") as target:
        target.write(struct.pack("<4sII", b"glTF", 2, total_length))
        target.write(struct.pack("<I4s", len(json_chunk), b"JSON"))
        target.write(json_chunk)
        target.write(struct.pack("<I4s", len(binary), b"BIN\x00"))
        target.write(binary)

    print(
        "Generated {0} ({1:.1f} MB); meshes={2}, materials={3}, triangles={4}".format(
            OUTPUT,
            os.path.getsize(OUTPUT) / (1024.0 * 1024.0),
            len(gltf_meshes),
            len(MATERIALS),
            sum(len(part.indices) // 3 for mesh in builders for part in mesh.parts.values()),
        )
    )


def generate():
    builders = [
        _make_terrain(),
        _make_roads(),
        _make_vegetation(),
        _make_buildings(),
        _make_props(),
    ]
    _write_glb(builders)


if __name__ == "__main__":
    generate()
