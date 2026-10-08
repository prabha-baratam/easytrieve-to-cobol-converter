from dataclasses import dataclass, field
import re
from typing import Dict, List, Optional


@dataclass
class FieldDefinition:
    name: str
    length: int
    type_code: str

    @property
    def cobol_pic(self) -> str:
        if self.type_code.upper() in {"A", "X"}:
            return f"X({self.length})"
        if self.type_code.upper() == "N":
            return f"9({self.length})"
        return "X(1)"


@dataclass
class FileDefinition:
    name: str
    fields: List[FieldDefinition] = field(default_factory=list)


@dataclass
class ProgramDefinition:
    files: List[FileDefinition]
    logic: List[str] = field(default_factory=list)


def parse_easytrieve(source: str) -> ProgramDefinition:
    """Parse a simplified Easytrieve program into a neutral program model."""
    files: List[FileDefinition] = []

    file_blocks = re.findall(r"FILE\s+(\w+)\s*(.*?)\s*END-FILE", source, flags=re.DOTALL | re.IGNORECASE)
    for name, body in file_blocks:
        fields: List[FieldDefinition] = []
        for line in body.splitlines():
            match = re.match(r"^\s*(\w+)\s+(\d+)\s+([A-Z])\s*$", line, flags=re.IGNORECASE)
            if match:
                field_name, length, type_code = match.groups()
                fields.append(FieldDefinition(field_name, int(length), type_code.upper()))
        files.append(FileDefinition(name=name, fields=fields))

    logic_blocks = re.findall(r"READ\s+(\w+)\s*(.*?)(?=END-PROGRAM|$)", source, flags=re.DOTALL | re.IGNORECASE)
    logic = []
    for _, body in logic_blocks:
        normalized = body.strip()
        if normalized:
            logic.append(normalized)

    return ProgramDefinition(files=files, logic=logic)


def convert_easytrieve_to_cobol(source: str) -> str:
    program = parse_easytrieve(source)

    if not program.files:
        raise ValueError("No FILE blocks found in the Easytrieve source.")

    lines: List[str] = []
    lines.append("IDENTIFICATION DIVISION.")
    lines.append("PROGRAM-ID. CONVERTED-PROGRAM.")
    lines.append("")
    lines.append("ENVIRONMENT DIVISION.")
    lines.append("INPUT-OUTPUT SECTION.")
    lines.append("FILE-CONTROL.")

    for file_def in program.files:
        lines.append(f"    SELECT {file_def.name} ASSIGN TO '{file_def.name}.DAT'")
        lines.append("        ORGANIZATION IS LINE SEQUENTIAL.")

    lines.append("")
    lines.append("DATA DIVISION.")
    lines.append("FILE SECTION.")

    for file_def in program.files:
        lines.append(f"FD  {file_def.name}.")
        lines.append(f"01  {file_def.name}-REC.")
        for field in file_def.fields:
            lines.append(f"    05  {field.name:<15} PIC {field.cobol_pic}.")

    lines.append("")
    lines.append("WORKING-STORAGE SECTION.")
    for file_def in program.files:
        lines.append(f"01  EOF-{file_def.name:<12} PIC X VALUE 'N'.")

    lines.append("")
    lines.append("PROCEDURE DIVISION.")
    for file_def in program.files:
        lines.append(f"    OPEN INPUT {file_def.name}")

    primary_file = program.files[0].name
    lines.append(f"    PERFORM UNTIL EOF-{primary_file} = 'Y'")
    lines.append(f"        READ {primary_file}")
    lines.append("           AT END")
    lines.append(f"              MOVE 'Y' TO EOF-{primary_file}")
    lines.append("           NOT AT END")

    if program.logic:
        for log in program.logic:
            normalized = log.strip()
            if normalized:
                lines.append(f"              {normalized}")
    else:
        lines.append("              CONTINUE")

    lines.append("        END-READ")
    lines.append("    END-PERFORM")

    for file_def in program.files:
        lines.append(f"    CLOSE {file_def.name}")

    lines.append("    STOP RUN.")
    return "\n".join(lines) + "\n"


__all__ = [
    "FieldDefinition",
    "FileDefinition",
    "ProgramDefinition",
    "parse_easytrieve",
    "convert_easytrieve_to_cobol",
]
