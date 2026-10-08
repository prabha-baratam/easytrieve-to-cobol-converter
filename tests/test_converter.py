import argparse
from pathlib import Path

from easytrieve_to_cobol.converter import convert_easytrieve_to_cobol


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert Easytrieve code to COBOL")
    parser.add_argument("input", type=str, help="Path to the Easytrieve source file")
    parser.add_argument("-o", "--output", type=str, help="Output COBOL file path")
    args = parser.parse_args()

    source_text = Path(args.input).read_text(encoding="utf-8")
    output_text = convert_easytrieve_to_cobol(source_text)

    if args.output:
        Path(args.output).write_text(output_text, encoding="utf-8")
    else:
        print(output_text)


if __name__ == "__main__":
    main()
