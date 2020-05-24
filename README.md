# [Password Store](https://www.passwordstore.org/) importer for 1password.

Creates file name based on Tag/Name

If the file already exists (when multiple entries from 1password with the same tag and name), they will be named Tag/Name2, 3, etc.

Password store should be empty to avoid potential problems I did not account for.

## Usage

`python3 import.py /path/to/1password/export/data.1pif`

## Issues

I'm unlikely to ever fix any created issues, but feel free to submit a PR.
