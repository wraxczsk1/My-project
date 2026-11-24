# Warfront development log

## 0.1.0

- Added the generated 12 km battlefield with terrain, forests, towns, roads,
  ruins, vehicles, and battlefield props.
- Added a main menu, loading screen, and a working single-player entry.
- Added runtime sky, clouds, sunlight, and atmospheric fog for gameplay maps.
- Added a development log and GitHub release update checks.
- Multiplayer remains unavailable.
- Fixed the packaged game startup and DirectX fallback.
- Improved the Singleplayer transition from the main menu to gameplay.

## 0.1.2

- Added a dedicated `Warfront-Game` launcher folder.
- Redesigned the main menu and loading screen.
- Verified a DirectX launch path for the packaging build.

## 0.1.3

- Rebuilt and saved the 12 km battlefield `.umap` from actual 3D mesh layers.
- Repaired the Unreal Python map generation collision setup.
- Moved the PlayerStart above the generated terrain.
- Added English menu, settings quality presets and grid inventory.
- Removed duplicate split-screen viewport rendering.
- Added lower-cost graphics defaults for a smoother Windows build.