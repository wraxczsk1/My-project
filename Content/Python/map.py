"""Place the generated Warfront battlefield as a playable Unreal level."""

import unreal


MAP_PREFIX = "WF_MapGen_"
_ACTORS = None


def _vector(location):
    return unreal.Vector(
        float(location[0]),
        float(location[1]),
        float(location[2]),
    )


def _spawn_actor(actor_class, label, location, rotation=None):
    actor = _ACTORS.spawn_actor_from_class(actor_class, _vector(location))
    if not actor:
        raise RuntimeError("Nepodarilo se vytvorit actor: " + label)
    if rotation is not None:
        actor.set_actor_rotation(
            unreal.Rotator(
                float(rotation[0]),
                float(rotation[1]),
                float(rotation[2]),
            ),
            False,
        )
    actor.set_actor_label(MAP_PREFIX + label)
    return actor


def _clear_previous_map():
    for actor in _ACTORS.get_all_level_actors():
        if actor.get_actor_label().startswith(MAP_PREFIX):
            if not _ACTORS.destroy_actor(actor):
                raise RuntimeError(
                    "Nepodarilo se odstranit predchozi actor: "
                    + actor.get_actor_label()
                )


def _set_complex_collision(mesh):
    body_setup = mesh.get_editor_property("body_setup")
    if not body_setup:
        raise RuntimeError("Mesh nema BodySetup pro kolize: " + mesh.get_path_name())

    collision_enum = getattr(unreal, "CollisionTraceFlag", None)
    if not collision_enum:
        raise RuntimeError("Unreal CollisionTraceFlag neni dostupny.")
    flag_name = next(
        (
            name
            for name in dir(collision_enum)
            if "COMPLEX_AS_SIMPLE" in name.upper()
        ),
        None,
    )
    if not flag_name:
        raise RuntimeError("CollisionTraceFlag nema volbu complex-as-simple.")

    body_setup.set_editor_property(
        "collision_trace_flag",
        getattr(collision_enum, flag_name),
    )
    mesh.mark_package_dirty()
    if not unreal.EditorAssetLibrary.save_asset(mesh.get_path_name(), False):
        raise RuntimeError("Nepodarilo se ulozit kolize meshe: " + mesh.get_path_name())


def _spawn_mesh(mesh, label, collision):
    actor = _spawn_actor(unreal.StaticMeshActor, label, (0.0, 0.0, 0.0))
    component = actor.get_component_by_class(unreal.StaticMeshComponent)
    if not component:
        raise RuntimeError("StaticMeshActor nema StaticMeshComponent: " + label)
    component.set_static_mesh(mesh)
    if collision:
        component.set_collision_profile_name("BlockAll")
        component.set_collision_enabled(
            unreal.CollisionEnabled.QUERY_AND_PHYSICS
        )
    else:
        component.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
    return actor


def _build_sky():
    _spawn_actor(unreal.SkyAtmosphere, "SkyAtmosphere", (0.0, 0.0, 0.0))

    sun = _spawn_actor(
        unreal.DirectionalLight,
        "Sun",
        (0.0, 0.0, 50000.0),
        (-8.0, -35.0, 0.0),
    )
    sun_component = sun.get_component_by_class(unreal.DirectionalLightComponent)
    if not sun_component:
        raise RuntimeError("Slunecni svetlo nema DirectionalLightComponent.")
    sun_component.set_editor_property("intensity", 35000.0)
    sun_component.set_editor_property("light_color", unreal.Color(255, 142, 92, 255))
    sun_component.set_editor_property("atmosphere_sun_light", True)
    sun_component.set_editor_property("atmosphere_sun_light_index", 0)

    sky_light = _spawn_actor(unreal.SkyLight, "SkyLight", (0.0, 0.0, 1000.0))
    sky_component = sky_light.get_component_by_class(unreal.SkyLightComponent)
    if not sky_component:
        raise RuntimeError("SkyLight nema SkyLightComponent.")
    sky_component.set_editor_property("mobility", unreal.ComponentMobility.MOVABLE)
    sky_component.recapture_sky()

    _spawn_actor(unreal.ExponentialHeightFog, "AtmosphericFog", (0.0, 0.0, 0.0))
    cloud_material = unreal.load_object(
        None,
        "/Engine/EngineSky/VolumetricClouds/"
        "m_SimpleVolumetricCloud_Inst.m_SimpleVolumetricCloud_Inst",
    )
    if not cloud_material:
        unreal.log_warning("Volumetricni cloud material nebyl nalezen.")
    else:
        clouds = _spawn_actor(
            unreal.VolumetricCloud,
            "VolumetricClouds",
            (0.0, 0.0, 180000.0),
        )
        cloud_component = clouds.get_component_by_class(
            unreal.VolumetricCloudComponent
        )
        if not cloud_component:
            raise RuntimeError("VolumetricCloud nema VolumetricCloudComponent.")
        cloud_component.set_material(cloud_material)


def _ensure_player_start():
    for actor in _ACTORS.get_all_level_actors():
        if isinstance(actor, unreal.PlayerStart):
            if not _ACTORS.destroy_actor(actor):
                raise RuntimeError("Nepodarilo se nahradit PlayerStart.")
    start = _spawn_actor(
        unreal.PlayerStart,
        "PlayerStart",
        (0.0, 0.0, 12000.0),
        (0.0, 90.0, 0.0),
    )
    start.set_actor_label(MAP_PREFIX + "PlayerStart")


def generate_ai_map(meshes, equipment=None):
    """Replace the old splat-only level with terrain and separate 3D map layers."""
    global _ACTORS

    if not isinstance(meshes, dict):
        raise TypeError("Map generator ocekava slovnik importovanych StaticMesh assetu.")
    required = ("terrain", "roads", "vegetation", "buildings", "battlefieldprops")
    missing = [name for name in required if not isinstance(meshes.get(name), unreal.StaticMesh)]
    if missing:
        raise RuntimeError("Chybi importovane 3D vrstvy mapy: " + ", ".join(missing))

    _ACTORS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    if not _ACTORS:
        raise RuntimeError("EditorActorSubsystem neni dostupny.")

    _clear_previous_map()
    _set_complex_collision(meshes["terrain"])
    _set_complex_collision(meshes["buildings"])
    _set_complex_collision(meshes["battlefieldprops"])

    _spawn_mesh(meshes["terrain"], "Terrain_12km", collision=True)
    _spawn_mesh(meshes["roads"], "ForestRoadNetwork", collision=False)
    _spawn_mesh(meshes["vegetation"], "Forests_And_Trees", collision=False)
    _spawn_mesh(meshes["buildings"], "Cities_And_Ruins", collision=True)
    _spawn_mesh(meshes["battlefieldprops"], "WarProps_And_Wrecks", collision=True)
    if isinstance(equipment, dict):
        if equipment.get("soldiers"):
            for index in range(12):
                actor = _spawn_mesh(
                    equipment["soldiers"],
                    "Soldier_" + str(index),
                    collision=True,
                )
                actor.set_actor_location(
                    _vector((-180.0 + index * 48.0, 30.0 * (1 if index % 2 else -1), 10600.0)),
                    False,
                    False,
                )
        if equipment.get("tanks"):
            actor = _spawn_mesh(equipment["tanks"], "Tank_CzechInspired", collision=True)
            actor.set_actor_location(_vector((900.0, -600.0, 10600.0)), False, False)
        if equipment.get("cars"):
            actor = _spawn_mesh(equipment["cars"], "Truck_CzechInspired", collision=True)
            actor.set_actor_location(_vector((-900.0, 500.0, 10600.0)), False, False)
    _build_sky()
    _ensure_player_start()

    unreal.log(
        "Warfront AI mapa hotova: 12 x 12 km, skutecny nerovny 3D teren, "
        "lesni cesty, lesy, mesta, ruiny, vozidla a hratelny PlayerStart."
    )
