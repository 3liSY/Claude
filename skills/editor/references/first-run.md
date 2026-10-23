# First run on his PC (checklist)

Do these in order. Stop at the first thing that fails and use `references/resolve-bridge.md` → "If the self-test fails".

1. Unzip so the folder is `%USERPROFILE%\.claude\skills\editor`. Open Claude Code and type `/editor`.
2. Say yes to first-time setup. Approve each install one at a time (ffmpeg, Python packages, faster-whisper, a headless browser if none is found).
3. Approve copying the bridge into Resolve's Scripts folder.
4. In Resolve: open ANY test project. Workspace > Scripts > Editor Bridge. Leave it running.
5. Run the self-test. It uses a throwaway timeline. Write each YES / NO into `brain/selftest.json`.
   - The five checks that matter most: placing a clip at the exact frame, clip length, zoom on a copy, Fusion smooth zoom, deleting only what it placed.
6. Add his library folders (his own B-roll and SFX). Index them.
7. Test video: open the finished timeline in Resolve. Run `/editor`. Pick SRB Gamer or Syrian Rubik.
8. Check the plan sheet and the short list. Approve only a few edits at first (for example 10).
9. Apply. In Resolve: Shift+Up / Shift+Down jumps between markers. Check: zoom timing, sound level, the Arabic pop-up cards, and that his own clips did not move.
10. Fine-tune by hand. Tell Claude "done". It learns and tells him what it learned.
11. If anything looks wrong: ask Claude to "undo everything" (it removes only its own clips), or open the backup timeline made on the first apply.
