# Image Steganography Studio

A user-friendly Tkinter desktop application for hiding secret text inside images and decoding it later.

## Why this project exists

This project demonstrates practical image steganography with a clean graphical interface, modular Python architecture, and open-source collaboration files ready for public contributions.

## Features

- Encode text inside an image with a desktop GUI.
- Decode hidden text from a previously encoded image.
- Capacity display so users know how much text an image can hold.
- Safer guidance for lossless formats like PNG and BMP.
- SOLID-oriented structure with separated UI, domain logic, validation, and persistence responsibilities.
- Open-source ready repository metadata, contribution guides, templates, and CI workflow.

## Tech stack

- Python 3.10+
- Tkinter
- Pillow

## Project structure

- [main.py](main.py) — GUI launcher.
- [steganography/gui.py](steganography/gui.py) — Tkinter user interface.
- [steganography/services.py](steganography/services.py) — encoding, decoding, validation, and image storage services.
- [steganography/models.py](steganography/models.py) — request models.
- [steganography/exceptions.py](steganography/exceptions.py) — domain exceptions.
- [requirements.txt](requirements.txt) — runtime dependency list.
- [pyproject.toml](pyproject.toml) — package metadata for Python tooling.

## SOLID design notes

The codebase applies the SOLID principles in a practical way:

- **Single Responsibility**: GUI logic, validation, image access, and steganography encoding are isolated in separate classes.
- **Open/Closed**: New storage backends or encoding algorithms can be introduced without rewriting the GUI.
- **Liskov Substitution**: The service layer depends on clear behavior contracts between collaborators.
- **Interface Segregation**: The GUI only uses the high-level service methods it needs.
- **Dependency Inversion**: The app composes dependencies through `build_default_service()` instead of hard-coding everything inside the window callbacks.

## Installation

1. Create and activate a virtual environment.
2. Install dependencies.
3. Launch the app.

Example on Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py
```

## How to use

### Encode a message

1. Open the app.
2. Choose **Encode Message**.
3. Select a source image.
4. Enter the secret message.
5. Pick an output path.
6. Save the encoded image.

### Decode a message

1. Open the app.
2. Choose **Decode Message**.
3. Select the encoded image.
4. Click **Decode**.
5. Copy the revealed text if needed.

## Important notes

- Prefer **PNG**, **BMP**, or **TIFF** for encoded output.
- Avoid lossy formats such as JPG for final encoded files because they can destroy hidden data.
- Capacity is approximately one character per three pixels.
- This project is intended for learning and benign privacy use cases, not for bypassing security controls.

## Screenshots

Add screenshots to [docs/assets](docs/assets) and update this section after publishing.

Suggested files:

- `docs/assets/encode-screen.png`
- `docs/assets/decode-screen.png`

## Open-source contribution guide

This repository includes:

- [CONTRIBUTING.md](CONTRIBUTING.md)
- [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)
- [SECURITY.md](SECURITY.md)
- [CHANGELOG.md](CHANGELOG.md)
- [CITATION.cff](CITATION.cff)
- [PUBLISHING.md](PUBLISHING.md)
- issue templates and pull request template under [.github](.github)

## Recommended GitHub repository settings for visibility

After creating the public repository, enable or add:

- A clear repository description.
- Topics such as `python`, `tkinter`, `steganography`, `pillow`, `gui`, `desktop-app`.
- A social preview image.
- Discussions for community interaction.
- Issues and pull requests.
- A pinned repository entry on your GitHub profile.
- A short demo GIF or screenshots in the README.
- Release tags for major versions.

## Suggested first public release checklist

- [ ] Add screenshots.
- [ ] Add the repository URL to [CITATION.cff](CITATION.cff).
- [ ] Add CI and status badges once the GitHub repository exists.
- [ ] Add a demo GIF to improve discoverability.
- [ ] Create `good first issue` tickets for contributors.
- [ ] Publish a `v1.0.0` release.

## Local development

Install dependencies and run:

```powershell
python main.py
```

## Basic quality check

```powershell
python -m compileall .
```

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE).
