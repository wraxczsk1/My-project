import importlib.util
import math
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MAP_SCRIPT = ROOT / "Scripts" / "generate_warfront_map.py"
OUTPUT = ROOT / "Content" / "Warfront" / "Models" / "WarfrontEquipment.glb"


def load_map_generator():
    spec = importlib.util.spec_from_file_location("warfront_map_generator", MAP_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("Nelze nacist mapovy generator.")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def make_soldier(w, center, facing=0.0):
    x, y, z = center
    w._add_box(w.builder, "concrete", (x, y + 24.0, z), (24.0, 46.0, 14.0), facing)
    w._add_ellipsoid(w.builder, "metal", (x, y + 53.0, z), (10.0, 10.0, 10.0), 10, 5)
    w._add_box(w.builder, "metal", (x, y + 59.0, z), (24.0, 7.0, 20.0), facing)
    w._add_box(w.builder, "roof", (x - 7.0, y + 11.0, z), (8.0, 34.0, 9.0), facing)
    w._add_box(w.builder, "roof", (x + 7.0, y + 11.0, z), (8.0, 34.0, 9.0), facing)
    w._add_box(w.builder, "leaves_dark", (x, y + 34.0, z - 10.0), (30.0, 26.0, 8.0), facing)
    weapon_start = (x + 14.0, y + 34.0, z - 18.0)
    weapon_end = (x + 14.0, y + 34.0, z - 85.0)
    w._add_cylinder_between(w.builder, "metal", weapon_start, weapon_end, 2.2, 8)


def make_rifle(w, center):
    x, y, z = center
    w._add_box(w.builder, "metal", (x, y, z), (9.0, 9.0, 78.0), 0.0)
    w._add_box(w.builder, "bark", (x, y - 3.0, z - 18.0), (10.0, 12.0, 28.0), 0.0)
    w._add_cylinder_between(w.builder, "metal", (x, y + 2.0, z - 40.0), (x, y + 2.0, z - 62.0), 3.0, 8)
    w._add_box(w.builder, "window", (x, y + 10.0, z - 12.0), (7.0, 5.0, 13.0), 0.0)


def make_tank(w, center):
    x, y, z = center
    w._add_box(w.builder, "metal", (x, y + 18.0, z), (96.0, 18.0, 58.0), 0.0)
    w._add_box(w.builder, "metal", (x, y + 34.0, z), (58.0, 22.0, 44.0), 0.0)
    w._add_cylinder_between(w.builder, "metal", (x, y + 38.0, z - 18.0), (x, y + 38.0, z - 105.0), 5.0, 10)
    for side in (-1.0, 1.0):
        for wheel_x in (-34.0, -17.0, 0.0, 17.0, 34.0):
            w._add_cylinder_between(
                w.builder,
                "roof",
                (x + wheel_x, y + 8.0, z + side * 32.0),
                (x + wheel_x, y + 8.0, z + side * 38.0),
                10.0,
                10,
            )


def make_truck(w, center):
    x, y, z = center
    w._add_box(w.builder, "metal", (x, y + 16.0, z), (70.0, 20.0, 38.0), 0.0)
    w._add_box(w.builder, "roof", (x - 18.0, y + 31.0, z), (34.0, 18.0, 36.0), 0.0)
    for wheel_x in (-24.0, 24.0):
        for side in (-1.0, 1.0):
            w._add_cylinder_between(
                w.builder,
                "roof",
                (x + wheel_x, y + 7.0, z + side * 20.0),
                (x + wheel_x, y + 7.0, z + side * 25.0),
                8.0,
                10,
            )


def main():
    generator = load_map_generator()
    generator.OUTPUT = OUTPUT

    class Equipment:
        builder = generator.MeshBuilder("Soldiers")

    Equipment.builder = generator.MeshBuilder("Soldiers")
    for index in range(8):
        make_soldier(type("W", (), {"builder": Equipment.builder, "_add_box": generator._add_box, "_add_ellipsoid": generator._add_ellipsoid, "_add_cylinder_between": generator._add_cylinder_between}), (-180.0 + index * 48.0, 0.0, -30.0 if index % 2 == 0 else 30.0))

    rifle = generator.MeshBuilder("CzechWeapons")
    make_rifle(type("W", (), {"builder": rifle, "_add_box": generator._add_box, "_add_cylinder_between": generator._add_cylinder_between}), (0.0, 25.0, 0.0))

    tank = generator.MeshBuilder("Tanks")
    make_tank(type("W", (), {"builder": tank, "_add_box": generator._add_box, "_add_cylinder_between": generator._add_cylinder_between}), (0.0, 0.0, 0.0))

    truck = generator.MeshBuilder("Cars")
    make_truck(type("W", (), {"builder": truck, "_add_box": generator._add_box, "_add_cylinder_between": generator._add_cylinder_between}), (0.0, 0.0, 0.0))

    generator._write_glb([Equipment.builder, rifle, tank, truck])


if __name__ == "__main__":
    main()
