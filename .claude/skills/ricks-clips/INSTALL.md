# Install

1. Unzip the release to a folder with no special characters in the path. Example: `C:\RicksClips_Skill_V1.1`.
2. Install the three.js kit packages (this installs the pinned GLTFLoader add-on used for imported GLB/glTF assets and the Asset Hub's PBR maps):
   ```
   cd templates/threejs_film
   npm install
   ```
3. Install the Python packages:
   ```
   pip install pillow numpy faster-whisper
   ```
4. Check ffmpeg: type `ffmpeg -version`. If it fails, install ffmpeg and add it to PATH.
5. Save your Fish Audio key. Make a file `%USERPROFILE%\.fish_api_key`. Put the key on the first line. Nothing else.
6. Set your sound folders. Some files hold the placeholders `<YOUR_SFX_FOLDER>` and `<YOUR_MUSIC_FOLDER>`. Replace them with your real folders. The files are:
   - `CB_RULES.md` and `rules/CB_RULES.md`
   - `SKILL.md`
   - `agents/sound-designer.md`
   - `rules/dept/lead.md`, `sound-designer.md`, `camera-director.md`, `stretch-builder.md`, `vfx-artist.md`, `background-painter.md`
   - `examples/lightning-spear/sound/clipdefs.py`

   Do this step before step 7 if you want the installed copy to show your folders.
7. Run the installer from the skill folder:
   ```
   python install.py
   ```
   It fills in the real path of this folder (`<SKILL_ROOT>`) in every text file. It installs the skill to `~/.claude/skills/ricks-clips-v1-1/` and the agents to `~/.claude/agents/`. It prints what it did. You can run it again any time. It also works after you move the folder.
8. Review `docs/ASSET_HUB.md`. For Sketchfab, provide your own OAuth access token in the current PowerShell session only when you want to download licensed, downloadable models. Fab products must be acquired and exported by you through Fab/Fab Launcher. Poly Haven and ambientCG public APIs do not require a token.
9. Open Claude Code in the skill folder. Paste this first prompt:

   > Read START_HERE.md and docs/ASSET_HUB.md, then make me a new Ricks Clips style short. Pitch me three true stories first.


## Final delivery check

After export, verify the required vertical format and frame rate with:

```bash
python tools/check_delivery.py episodes/<name>/final.mp4
```

The default gate expects 1080x1920 at 30 fps. Add `--require-audio` when the final MP4 must include an audio stream. This checks container metadata only; listen to the mix and inspect the finished video separately.
