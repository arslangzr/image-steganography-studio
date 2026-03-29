# Publishing Guide

This project is already prepared as a local git repository.

## Create the public GitHub repository

### Option 1: GitHub website

1. Go to GitHub.
2. Select **New repository**.
3. Repository name suggestion: `image-steganography-studio`.
4. Add a short description.
5. Set visibility to **Public**.
6. Do not initialize with a README, `.gitignore`, or license because this project already includes them.
7. Create the repository.

Then connect this local repository:

```powershell
git remote add origin https://github.com/<your-username>/image-steganography-studio.git
git push -u origin main
```

### Option 2: GitHub CLI

If GitHub CLI is installed later:

```powershell
gh auth login
gh repo create image-steganography-studio --public --source . --remote origin --push
```

## Recommended repository settings for discoverability

After publishing, configure the repository with:

- Description: `Tkinter desktop app for hiding and revealing messages inside images with Python and Pillow.`
- Website: add a project demo link later if available.
- Topics:
  - `python`
  - `tkinter`
  - `steganography`
  - `pillow`
  - `image-processing`
  - `desktop-app`
  - `gui`
- Enable Issues.
- Enable Discussions.
- Add a social preview image.
- Pin the repository on your GitHub profile.

## Visibility checklist

- Add screenshots to the README.
- Create at least 3 `good first issue` tickets.
- Add labels such as `good first issue`, `help wanted`, `bug`, and `enhancement`.
- Publish a first release `v1.0.0`.
- Share the repository on LinkedIn, X, Reddit communities, Dev.to, or Hashnode.
- Add a short demo video or GIF.
- Keep the README concise, visual, and keyword-rich.

## Suggested first GitHub issue ideas

- Add drag-and-drop support for images.
- Add unit tests for the service layer.
- Support message encryption before embedding.
- Add image preview thumbnails.
- Add dark mode styling.
