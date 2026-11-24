# Warfront

Warfront is a Windows single-player battlefield project for Unreal Engine 5.8.
The multiplayer menu is a placeholder and online play is not available yet.

## Open and play

1. Install Unreal Engine 5.8.
2. Open `Warfront.uproject` and let the editor build the `Warfront` module.
3. Use **Play** in the editor, or build a packaged Windows version with
   `Scripts/package_windows.ps1`.

The generated battlefield source is `Content/Warfront/Maps/WarfrontAIMap.glb`.
The editor startup script imports changed map data and rebuilds
`Content/Maps/WarfrontMap.umap`. The runtime weather subsystem adds sky,
volumetric clouds, sunlight, and fog to gameplay maps that do not already
contain them.

Controls: WASD to move, mouse to look, Space to jump.

## Windows package

Run this from PowerShell:

```powershell
.\Scripts\package_windows.ps1
```

The packaged game and `Warfront-Windows.zip` are written under `Build`.
Generated packages and Unreal build intermediates are intentionally not
committed to the source repository.

## Updates

The game checks the public GitHub Releases page for a newer version.
To publish an update:

1. Increase `ProjectVersion` in `Config/DefaultGame.ini`.
2. Package the game with the script above.
3. Create a GitHub Release with a tag such as `v0.2.0`.
4. Attach the generated `Warfront-Windows.zip`.

The in-game updater asks before downloading, verifies GitHub's SHA-256 asset
digest, waits for the game to close, applies the package, and restarts it.

## Development log

See [DEVLOG.md](DEVLOG.md).
