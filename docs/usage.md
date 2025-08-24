# Usage

This project provides a simple, configuration-driven agent application.

## Running the demo

1. Ensure dependencies are installed:
   ```bash
   poetry install
   ```
2. Execute the demo script:
   ```bash
   poetry run python demo.py
   ```
   The script reads `config.yaml` and prints the processed text.

## Custom configuration

Modify `config.yaml` to adjust the `input_text` or the list of `operations`.

Available operations:

- `uppercase`: convert text to uppercase.
- `prefix`: prepend text with the specified `value` parameter.
