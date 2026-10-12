# SMILES Learning App

A small Streamlit classroom app that teaches SMILES notation. Students see molecules of increasing complexity (drawn with RDKit), type the SMILES string, and get balloons on success.

Molecule list lives in `molecules.yaml` — edit that file to change the lesson.

## Local development (uv)

```bash
uv sync
uv run streamlit run app.py
```

After changing dependencies:

```bash
uv add <package>
uv export --no-dev --no-hashes -o requirements.txt
```

Streamlit Community Cloud installs from `requirements.txt`, not from uv, so keep that file in sync before pushing.

## Deploy (Streamlit Community Cloud)

1. Push this repo to GitHub.
2. Create an app on [share.streamlit.io](https://share.streamlit.io).
3. Set the main file to `app.py`.
4. Use Python 3.12 if prompted.

No secrets are required.

## Project layout

| File | Role |
|------|------|
| `app.py` | Streamlit entrypoint |
| `molecules.yaml` | Ordered challenges |
| `pyproject.toml` | Local deps (uv) |
| `requirements.txt` | Cloud deps (exported from uv) |
