# Agent Observer — profile card v4

Replace the files in Jas952/Jas952:
- assets/agent-observer-card.webp
- assets/agent-observer-card.svg
- assets/agent-observer-card.png
- scripts/render_card.py
- .github/workflows/update-project-card.yml

The workflow now installs fonts-inter and fonttools so the generator can outline Inter glyphs. The SVG contains vector paths; no font files are bundled or needed to view the assets. The existing README path is unchanged; use `?v=4` if a cached image is displayed.

2400 × 912 lossless animated WebP, 90 frames, 50 fps during motion, transparent exterior. Stars remain hidden until the live API fetch succeeds; workflow refreshes stars daily.
