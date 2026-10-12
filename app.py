"""SMILES learning app for classroom use."""

from __future__ import annotations

from pathlib import Path

import streamlit as st
import yaml
from rdkit import Chem, RDLogger
from rdkit.Chem import Draw

RDLogger.DisableLog("rdApp.*")

MOLECULES_PATH = Path(__file__).parent / "molecules.yaml"


@st.cache_data
def load_molecules(path: str) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    molecules = data.get("molecules") or []
    if not molecules:
        raise ValueError("No molecules found in YAML.")
    return molecules


def mol_from_smiles(smiles: str) -> Chem.Mol | None:
    if not smiles or not smiles.strip():
        return None
    return Chem.MolFromSmiles(smiles.strip())


def canonical_smiles(smiles: str) -> str | None:
    mol = mol_from_smiles(smiles)
    if mol is None:
        return None
    return Chem.MolToSmiles(mol)


def render_molecule_image(smiles: str, size: tuple[int, int] = (400, 300)):
    mol = mol_from_smiles(smiles)
    if mol is None:
        return None
    return Draw.MolToImage(mol, size=size)


def init_state(n_molecules: int) -> None:
    if "index" not in st.session_state:
        st.session_state.index = 0
    if "completed" not in st.session_state:
        st.session_state.completed = False
    if "feedback" not in st.session_state:
        st.session_state.feedback = None
    if "celebrate" not in st.session_state:
        st.session_state.celebrate = False
    if st.session_state.index >= n_molecules and not st.session_state.completed:
        st.session_state.index = max(0, n_molecules - 1)


def reset_lesson() -> None:
    st.session_state.index = 0
    st.session_state.completed = False
    st.session_state.feedback = None
    st.session_state.celebrate = False


def check_answer(student_smiles: str, answer_smiles: str) -> str:
    """Return 'invalid', 'wrong', or 'correct'."""
    student_can = canonical_smiles(student_smiles)
    if student_can is None:
        return "invalid"
    answer_can = canonical_smiles(answer_smiles)
    if answer_can is None:
        return "invalid"
    return "correct" if student_can == answer_can else "wrong"


def show_structure(smiles: str | None, empty_message: str) -> None:
    """Render a molecule image or a short status message."""
    if not smiles or not smiles.strip():
        st.info(empty_message)
        return
    image = render_molecule_image(smiles)
    if image is None:
        st.warning("Invalid SMILES — fix the string to see a structure.")
        return
    st.image(image, use_container_width=True)


def show_smiles_sidebar() -> None:
    """Basic SMILES reference for students who get stuck."""
    with st.sidebar:
        st.header("SMILES basics")
        st.caption("Quick reference — keep this open while you work.")

        st.subheader("Atoms")
        st.markdown(
            """
- Organic subset: `B`, `C`, `N`, `O`, `P`, `S`, `F`, `Cl`, `Br`, `I`
- Write them as-is: `C` = carbon, `O` = oxygen, `N` = nitrogen
- Hydrogens are usually **implied** (you rarely type `H`)
            """.strip()
        )

        st.subheader("Bonds")
        st.markdown(
            """
- Single bonds are **default** (no symbol): `CC` = ethane
- `=` double bond: `C=C` = ethene
- `#` triple bond: `C#C` = ethyne
            """.strip()
        )

        st.subheader("Branches")
        st.markdown(
            """
- Put side chains in parentheses: `CC(C)C` = isobutane
- Branches attach to the atom **just before** `(`
            """.strip()
        )

        st.subheader("Rings")
        st.markdown(
            """
- Mark ring closure with matching digits: `C1CCCCC1` = cyclohexane
- The digit links two atoms into a ring
            """.strip()
        )

        st.subheader("Aromatic")
        st.markdown(
            """
- Lowercase letters are aromatic: `c1ccccc1` = benzene
- Aromatic bonds are often left implicit inside the ring
            """.strip()
        )

        st.subheader("Tiny examples")
        st.code(
            "C        methane\n"
            "CCO      ethanol\n"
            "CC(=O)O  acetic acid\n"
            "c1ccccc1 benzene",
            language=None,
        )

        st.divider()
        st.markdown(
            "Tip: watch the **Your molecule** panel — if the drawing "
            "looks wrong, fix the SMILES before hitting Check."
        )


def main() -> None:
    st.set_page_config(page_title="Learn SMILES", page_icon="🧪", layout="wide")
    show_smiles_sidebar()
    st.title("Learn SMILES")
    st.caption("Match the target structure by typing SMILES. Compare both drawings as you go.")

    molecules = load_molecules(str(MOLECULES_PATH))
    init_state(len(molecules))

    if st.session_state.celebrate:
        st.balloons()
        st.session_state.celebrate = False

    if st.session_state.completed:
        st.success("You finished every molecule. Nice work!")
        if st.button("Start over"):
            reset_lesson()
            st.rerun()
        return

    idx = st.session_state.index
    mol_spec = molecules[idx]
    total = len(molecules)
    input_key = f"smiles_input_{mol_spec['id']}"

    st.progress(idx / total, text=f"Molecule {idx + 1} of {total}")
    st.subheader(mol_spec["name"])
    if mol_spec.get("difficulty"):
        st.caption(mol_spec["difficulty"])

    left, right = st.columns(2, gap="large")
    with left:
        st.markdown("**Target**")
        st.caption("Build a SMILES string for this structure.")
        show_structure(mol_spec["smiles"], "Missing target molecule in YAML.")
        if mol_spec.get("hint"):
            with st.expander("Hint"):
                st.write(mol_spec["hint"])

    with right:
        st.markdown("**Your molecule**")
        student = st.text_input(
            "SMILES",
            key=input_key,
            placeholder="e.g. CCO",
            help="Preview updates as you type. Equivalent SMILES spellings still count as correct.",
        )
        show_structure(student, "Start typing SMILES to preview your molecule.")
        check = st.button("Check", type="primary")

    if check:
        result = check_answer(student, mol_spec["smiles"])
        if result == "invalid":
            st.session_state.feedback = (
                "error",
                "That does not look like valid SMILES. Try again.",
            )
        elif result == "wrong":
            st.session_state.feedback = (
                "warning",
                "Valid SMILES, but not this molecule. Compare the two drawings and adjust.",
            )
        else:
            st.session_state.feedback = ("success", "Correct!")
            st.session_state.celebrate = True
            if idx + 1 >= total:
                st.session_state.completed = True
            else:
                st.session_state.index = idx + 1
            st.rerun()

    feedback = st.session_state.feedback
    if feedback:
        kind, message = feedback
        if kind == "error":
            st.error(message)
        elif kind == "warning":
            st.warning(message)
        else:
            st.success(message)
            st.session_state.feedback = None


if __name__ == "__main__":
    main()
