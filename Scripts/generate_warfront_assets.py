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


def make_pistol(w, center):
    x, y, z = center
    w._add_box(w.builder, "metal", (x, y, z), (11.0, 8.0, 34.0), 0.0)
    w._add_box(w.builder, "bark", (x, y - 9.0, z - 8.0), (9.0, 18.0, 16.0), 0.0)
    w._add_cylinder_between(w.builder, "metal", (x, y + 1.0, z - 17.0), (x, y + 1.0, z - 28.0), 2.2, 8)


def make_helmet(w, center):
    x, y, z = center
    w._add_ellipsoid(w.builder, "leaves_dark", (x, y + 10.0, z), (24.0, 16.0, 24.0), 12, 7)
    w._add_box(w.builder, "metal", (x, y - 2.0, z - 20.0), (48.0, 7.0, 28.0), 0.0)


def make_vest(w, center):
    x, y, z = center
    w._add_box(w.builder, "leaves_dark", (x, y + 18.0, z), (48.0, 22.0, 54.0), 0.0)
    w._add_box(w.builder, "metal", (x - 27.0, y + 18.0, z), (9.0, 18.0, 42.0), 0.0)
    w._add_box(w.builder, "metal", (x + 27.0, y + 18.0, z), (9.0, 18.0, 42.0), 0.0)
    w._add_box(w.builder, "roof", (x, y - 2.0, z - 29.0), (44.0, 12.0, 8.0), 0.0)


def make_patches(w, center):
    x, y, z = center
    w._add_box(w.builder, "window", (x - 10.0, y, z), (16.0, 5.0, 11.0), 0.0)
    w._add_box(w.builder, "roof", (x + 10.0, y, z), (16.0, 5.0, 11.0), 0.0)
    w._add_box(w.builder, "concrete", (x, y + 7.0, z), (34.0, 5.0, 10.0), 0.0)


def make_apc(w, center):
    x, y, z = center
    w._add_box(w.builder, "leaves_dark", (x, y + 18.0, z), (118.0, 28.0, 72.0), 0.0)
    w._add_box(w.builder, "leaves_light", (x - 18.0, y + 38.0, z), (72.0, 18.0, 58.0), 0.0)
    w._add_cylinder_between(w.builder, "metal", (x + 20.0, y + 44.0, z - 25.0), (x + 20.0, y + 44.0, z - 72.0), 4.5, 10)
    for wheel_x in (-42.0, -14.0, 14.0, 42.0):
        for side in (-1.0, 1.0):
            w._add_cylinder_between(
                w.builder,
                "roof",
                (x + wheel_x, y + 8.0, z + side * 36.0),
                (x + wheel_x, y + 8.0, z + side * 43.0),
                12.0,
                10,
            )


def make_truck_camo(w, center):
    x, y, z = center
    w._add_box(w.builder, "leaves_dark", (x, y + 16.0, z), (78.0, 22.0, 42.0), 0.0)
    w._add_box(w.builder, "leaves_light", (x - 24.0, y + 34.0, z), (40.0, 20.0, 38.0), 0.0)
    w._add_box(w.builder, "bark", (x + 18.0, y + 23.0, z + 24.0), (36.0, 12.0, 6.0), 0.0)
    for wheel_x in (-28.0, 28.0):
        for side in (-1.0, 1.0):
            w._add_cylinder_between(
                w.builder,
                "roof",
                (x + wheel_x, y + 7.0, z + side * 22.0),
                (x + wheel_x, y + 7.0, z + side * 27.0),
                9.0,
                10,
            )


def make_helicopter(w, center):
    x, y, z = center
    w._add_box(w.builder, "leaves_dark", (x, y + 16.0, z), (86.0, 24.0, 46.0), 0.0)
    w._add_cylinder_between(w.builder, "metal", (x, y + 34.0, z), (x, y + 34.0, z - 95.0), 4.0, 10)
    w._add_box(w.builder, "metal", (x, y + 46.0, z), (150.0, 3.0, 8.0), 0.0)
    w._add_box(w.builder, "metal", (x, y + 46.0, z), (8.0, 3.0, 150.0), 0.0)
    w._add_box(w.builder, "roof", (x + 62.0, y + 18.0, z), (38.0, 8.0, 18.0), 0.0)


def make_drone(w, center):
    x, y, z = center
    w._add_box(w.builder, "metal", (x, y + 8.0, z), (42.0, 8.0, 16.0), 0.0)
    for sx in (-1.0, 1.0):
        w._add_box(w.builder, "metal", (x + sx * 32.0, y + 10.0, z), (28.0, 3.0, 5.0), 0.0)
        w._add_cylinder_between(w.builder, "roof", (x + sx * 32.0, y + 14.0, z), (x + sx * 32.0, y + 14.0, z - 18.0), 7.0, 8)


def make_aircraft(w, center):
    x, y, z = center
    w._add_box(w.builder, "metal", (x, y + 10.0, z), (38.0, 14.0, 118.0), 0.0)
    w._add_box(w.builder, "metal", (x, y + 12.0, z), (150.0, 4.0, 28.0), 0.0)
    w._add_box(w.builder, "leaves_dark", (x, y + 26.0, z - 28.0), (32.0, 8.0, 32.0), 0.0)


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

    pistol = generator.MeshBuilder("CzechPistol")
    make_pistol(type("W", (), {"builder": pistol, "_add_box": generator._add_box, "_add_cylinder_between": generator._add_cylinder_between}), (0.0, 25.0, 0.0))

    helmet = generator.MeshBuilder("CzechHelmet")
    make_helmet(type("W", (), {"builder": helmet, "_add_ellipsoid": generator._add_ellipsoid, "_add_box": generator._add_box}), (0.0, 0.0, 0.0))

    vest = generator.MeshBuilder("CzechVest")
    make_vest(type("W", (), {"builder": vest, "_add_box": generator._add_box}), (0.0, 0.0, 0.0))

    patches = generator.MeshBuilder("CzechPatches")
    make_patches(type("W", (), {"builder": patches, "_add_box": generator._add_box}), (0.0, 0.0, 0.0))

    apc = generator.MeshBuilder("CzechAPC")
    make_apc(type("W", (), {"builder": apc, "_add_box": generator._add_box, "_add_cylinder_between": generator._add_cylinder_between}), (0.0, 0.0, 0.0))

    camo_truck = generator.MeshBuilder("CzechCamoTruck")
    make_truck_camo(type("W", (), {"builder": camo_truck, "_add_box": generator._add_box, "_add_cylinder_between": generator._add_cylinder_between}), (0.0, 0.0, 0.0))

    helicopter = generator.MeshBuilder("CzechHelicopter")
    make_helicopter(type("W", (), {"builder": helicopter, "_add_box": generator._add_box, "_add_cylinder_between": generator._add_cylinder_between}), (0.0, 0.0, 0.0))

    drone = generator.MeshBuilder("CzechDrone")
    make_drone(type("W", (), {"builder": drone, "_add_box": generator._add_box, "_add_cylinder_between": generator._add_cylinder_between}), (0.0, 0.0, 0.0))

    aircraft = generator.MeshBuilder("CzechAircraft")
    make_aircraft(type("W", (), {"builder": aircraft, "_add_box": generator._add_box}), (0.0, 0.0, 0.0))

    generator._write_glb([
        Equipment.builder, rifle, tank, truck, pistol, helmet, vest, patches,
        apc, camo_truck, helicopter, drone, aircraft
    ])


if __name__ == "__main__":
    main()
