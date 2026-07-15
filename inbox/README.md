This folder receives .ris citation exports (Scopus / Web of Science / ScienceDirect).
Drop files here (GitHub web upload works from a phone). The weekly update — or
'python3 scripts/merge_ris.py' — merges their abstracts/keywords into the archive
by DOI/title match and moves processed files to processed/. Unmatched records are
ignored, existing data is never overwritten.
