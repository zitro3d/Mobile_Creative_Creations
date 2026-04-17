# Mobile Creative Creations — Claude Instructions

## Deploy workflow
After every commit to the feature branch, always merge to `main` and push so changes go live on GitHub Pages immediately:

```
git push -u origin claude/gesture-3d-space-game-1FalV
git checkout main
git merge claude/gesture-3d-space-game-1FalV --no-edit
git push origin main
git checkout claude/gesture-3d-space-game-1FalV
```

If merge conflicts occur on `main`, take the feature branch version (`git checkout --theirs`).

## Project
- Single file game: `vectorrocketpro.html`
- Three.js r160 via importmap CDN
- Feature branch: `claude/gesture-3d-space-game-1FalV`
- GitHub Pages deploys from `main` only
