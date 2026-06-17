# NHANES Data Files
Raw XPT files are not stored in this repository. Download:

```bash
python scripts/download_nhanes.py
```

Files go in data/raw/ — see docs/DATA_DICTIONARY.md for variable reference.

| File | Variables |
|---|---|
| DEMO_J.XPT | SEQN, RIDAGEYR, RIAGENDR, RIDRETH3, WTMEC2YR |
| TCHOL_J.XPT | LBXTC |
| HDL_J.XPT | LBDHDD |
| TRIGLY_J.XPT | LBDLDL, LBXTR |
| GHB_J.XPT | LBXGH (HbA1c — required) |
| GLU_J.XPT | LBXGLU, PHAFSTHR |
| BPX_J.XPT | BPXOSY1–3, BPXODI1–3 |
| BMX_J.XPT | BMXBMI |
| BPQ_J.XPT | BPQ050A, BPQ090D |
| DIQ_J.XPT | DIQ050, DIQ070 |
