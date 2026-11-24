"""Open, generate, and save the Warfront map whenever the editor starts."""

import importlib.util
import json
import os

import unreal


MAP_PACKAGE = "/Game/Maps/WarfrontMap"
MAP_FILE = os.path.join(
    unreal.Paths.project_content_dir(), "Maps", "WarfrontMap.umap"
)
BATTLEFIELD_FILE = os.path.join(
    unreal.Paths.project_content_dir(),
    "Warfront",
    "Maps",
    "WarfrontAIMap.glb",
)
BATTLEFIELD_ASSET_PATH = "/Game/Warfront/Maps/Generated"
LOGO_SOURCE = os.path.join(
    unreal.Paths.project_content_dir(),
    "Warfront",
    "UI",
    "GUI",
    "WarfrontLogo.png",
)
LOGO_ASSET_PATH = "/Game/Warfront/UI/GUI/WarfrontLogo.WarfrontLogo"
PROJECT_DIR = os.path.dirname(os.path.normpath(unreal.Paths.project_content_dir()))
STATE_DIR = os.path.join(PROJECT_DIR, "Saved")
STATE_FILE = os.path.join(STATE_DIR, "WarfrontMapGenerator.txt")
ASSET_STATE_FILE = os.path.join(STATE_DIR, "WarfrontAIMapAssets.json")
MAP_SCRIPT = os.path.join(os.path.dirname(__file__), "map.py")
REQUIRED_MESHES = (
    "terrain",
    "roads",
    "vegetation",
    "buildings",
    "battlefieldprops",
)


def _import_logo_if_needed():
    if not os.path.isfile(LOGO_SOURCE):
        unreal.log_warning("Warfront logo nebylo nalezeno: " + LOGO_SOURCE)
        return
    if unreal.EditorAssetLibrary.does_asset_exist(LOGO_ASSET_PATH):
        return

    import_task = unreal.AssetImportTask()
    import_task.set_editor_property("filename", LOGO_SOURCE)
    import_task.set_editor_property("destination_path", "/Game/Warfront/UI/GUI")
    import_task.set_editor_property("destination_name", "WarfrontLogo")
    import_task.set_editor_property("automated", True)
    import_task.set_editor_property("save", True)
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([import_task])

    if not unreal.EditorAssetLibrary.load_asset(LOGO_ASSET_PATH):
        raise RuntimeError("Nepodarilo se importovat logo Warfront: " + LOGO_SOURCE)


def _level_editor():
    subsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    if not subsystem:
        raise RuntimeError("LevelEditorSubsystem neni dostupny.")
    return subsystem


def _load_map_generator():
    spec = importlib.util.spec_from_file_location("warfront_map_generator", MAP_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("Nelze nacist generator mapy: " + MAP_SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _open_or_create_map():
    os.makedirs(os.path.dirname(MAP_FILE), exist_ok=True)
    level_editor = _level_editor()
    if os.path.isfile(MAP_FILE):
        level = level_editor.get_current_level()
        current_package = level.get_outermost().get_name() if level else ""
        if current_package != MAP_PACKAGE:
            if not level_editor.load_level(MAP_PACKAGE):
                raise RuntimeError("Nelze otevrit level: " + MAP_PACKAGE)
    elif not level_editor.new_level(MAP_PACKAGE):
        raise RuntimeError("Nelze vytvorit level: " + MAP_PACKAGE)


def _map_script_needs_to_run():
    if not os.path.isfile(MAP_FILE) or not os.path.isfile(STATE_FILE):
        return True
    with open(STATE_FILE, "r", encoding="utf-8") as state_file:
        state = state_file.read().splitlines()
    if len(state) != 2:
        return True
    last_script_mtime = float(state[0])
    last_source_mtime = float(state[1])
    if not os.path.isfile(BATTLEFIELD_FILE):
        raise RuntimeError("3D mapa nebyla nalezena: " + BATTLEFIELD_FILE)
    current_source_mtime = os.path.getmtime(BATTLEFIELD_FILE)
    return (
        os.path.getmtime(MAP_SCRIPT) > last_script_mtime
        or current_source_mtime > last_source_mtime
    )


def _load_cached_battlefield(mesh_mtime):
    if not os.path.isfile(ASSET_STATE_FILE):
        return None
    with open(ASSET_STATE_FILE, "r", encoding="utf-8") as state_file:
        asset_state = json.load(state_file)
    if asset_state.get("source_mtime") != mesh_mtime:
        return None

    paths = asset_state.get("assets", {})
    if any(name not in paths for name in REQUIRED_MESHES):
        return None

    meshes = {
        name: unreal.EditorAssetLibrary.load_asset(paths[name])
        for name in REQUIRED_MESHES
    }
    if all(isinstance(mesh, unreal.StaticMesh) for mesh in meshes.values()):
        return meshes
    return None


def _load_or_import_battlefield_meshes():
    if not os.path.isfile(BATTLEFIELD_FILE):
        raise RuntimeError("3D mapa nebyla nalezena: " + BATTLEFIELD_FILE)

    source_mtime = os.path.getmtime(BATTLEFIELD_FILE)
    cached_meshes = _load_cached_battlefield(source_mtime)
    if cached_meshes:
        return cached_meshes

    import_task = unreal.AssetImportTask()
    import_task.set_editor_property("filename", BATTLEFIELD_FILE)
    import_task.set_editor_property("destination_path", BATTLEFIELD_ASSET_PATH)
    import_task.set_editor_property("destination_name", "WarfrontAIMap")
    import_task.set_editor_property("replace_existing", True)
    import_task.set_editor_property("automated", True)
    import_task.set_editor_property("save", True)
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([import_task])

    imported_paths = import_task.get_editor_property("imported_object_paths")
    meshes = {}
    for asset_path in imported_paths:
        asset = unreal.EditorAssetLibrary.load_asset(asset_path)
        if isinstance(asset, unreal.StaticMesh):
            name = asset.get_name().lower()
            for category in REQUIRED_MESHES:
                if category in name:
                    if category in meshes:
                        raise RuntimeError(
                            "Import vytvořil více meshů pro vrstvu " + category
                        )
                    meshes[category] = asset

    missing = [name for name in REQUIRED_MESHES if name not in meshes]
    if missing:
        mesh_paths = [
            path
            for path in imported_paths
            if isinstance(unreal.EditorAssetLibrary.load_asset(path), unreal.StaticMesh)
        ]
        raise RuntimeError(
            "GLB neobsahuje ocekavane 3D vrstvy "
            + ", ".join(missing)
            + ". Importovane StaticMesh assety: "
            + ", ".join(mesh_paths)
        )

    os.makedirs(STATE_DIR, exist_ok=True)
    with open(ASSET_STATE_FILE, "w", encoding="utf-8") as state_file:
        json.dump(
            {
                "source_mtime": source_mtime,
                "assets": {
                    name: meshes[name].get_path_name()
                    for name in REQUIRED_MESHES
                },
            },
            state_file,
            indent=2,
        )
    return meshes


def generate_and_save_startup_map():
    _import_logo_if_needed()
    regenerate = _map_script_needs_to_run()
    _open_or_create_map()
    if regenerate:
        meshes = _load_or_import_battlefield_meshes()
        _load_map_generator().generate_ai_map(meshes)
        if not _level_editor().save_current_level():
            raise RuntimeError("Nepodarilo se ulozit level: " + MAP_PACKAGE)
        os.makedirs(STATE_DIR, exist_ok=True)
        with open(STATE_FILE, "w", encoding="utf-8") as state_file:
            state_file.write(str(os.path.getmtime(MAP_SCRIPT)) + "\n")
            state_file.write(str(os.path.getmtime(BATTLEFIELD_FILE)))
        unreal.log("Warfront 3D mapa byla importovana, vytvorena a ulozena.")
    else:
        unreal.log("Warfront 3D mapa nactena; neni treba ji znovu generovat.")


generate_and_save_startup_map()
