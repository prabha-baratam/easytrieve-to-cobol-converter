# easytrieve-to-cobol-converter

This repository contains a lightweight custom conversion agent for translating a subset of Easytrieve programs into COBOL.

## What it does

- Parses Easytrieve `FILE` definitions and field layouts
- Converts file and record definitions into COBOL `FD`/`01` declarations
- Generates a basic COBOL program skeleton
- Produces a readable COBOL output suitable for review and further refinement

## Example

Easytrieve input:

```easytrieve
FILE F1
  NAME 10 A
  SALES 5 N
END-FILE

READ F1
  IF SALES > 1000
    DISPLAY NAME SALES
  END-IF
END-PROGRAM
```

Converted COBOL output:

```cobol
IDENTIFICATION DIVISION.
PROGRAM-ID. CONVERTED-PROGRAM.

ENVIRONMENT DIVISION.
INPUT-OUTPUT SECTION.
FILE-CONTROL.
    SELECT F1 ASSIGN TO 'F1.DAT'
        ORGANIZATION IS LINE SEQUENTIAL.

DATA DIVISION.
FILE SECTION.
FD  F1.
01  F1-REC.
    05  NAME              PIC X(10).
    05  SALES             PIC 9(5).

WORKING-STORAGE SECTION.
01  EOF-F1               PIC X VALUE 'N'.

PROCEDURE DIVISION.
    OPEN INPUT F1
    PERFORM UNTIL EOF-F1 = 'Y'
        READ F1
           AT END
              MOVE 'Y' TO EOF-F1
           NOT AT END
              IF SALES > 1000
                  DISPLAY NAME SALES
              END-IF
        END-READ
    END-PERFORM
    CLOSE F1
    STOP RUN.
```

## Project structure

- `easytrieve_to_cobol/converter.py` - core conversion logic
- `easytrieve_to_cobol/cli.py` - command line entry point
- `tests/test_converter.py` - automated verification

## Usage

```bash
python -m easytrieve_to_cobol.cli input.et > output.cbl
```

Or use the Python API:

```python
from easytrieve_to_cobol.converter import convert_easytrieve_to_cobol

source = """
FILE F1
  NAME 10 A
  SALES 5 N
END-FILE

READ F1
  IF SALES > 1000
    DISPLAY NAME SALES
  END-IF
END-PROGRAM
"""

cobol = convert_easytrieve_to_cobol(source)
print(cobol)
```

## Notes

This is a practical starter implementation intended for a subset of Easytrieve syntax. For production-grade conversion of large enterprise programs, it is still recommended to pair this with vendor solutions like IBM Migration Utility, HTWC EZT2COB, or MigrationWare for broader language coverage and validation.
