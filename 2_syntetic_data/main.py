import sys

import config
from pipeline import run_all, run_single, show_status


def print_usage():
    print("Verwendung:")
    print("  uv run python main.py generate-all [--model MODEL]")
    print("  uv run python main.py generate-case CASE_ID [--model MODEL]")
    print("  uv run python main.py status")
    print()
    print(f"Default-Modell: {config.DEFAULT_MODEL}")


def parse_model(args: list[str]) -> str:
    """Extract --model value from args, return default if not present."""
    for i, arg in enumerate(args):
        if arg == "--model" and i + 1 < len(args):
            return args[i + 1]
    return config.DEFAULT_MODEL


def main():
    args = sys.argv[1:]

    if not args:
        print_usage()
        sys.exit(1)

    command = args[0]

    if command == "generate-all":
        model = parse_model(args[1:])
        run_all(model)

    elif command == "generate-case":
        if len(args) < 2:
            print("Fehler: CASE_ID fehlt.")
            print("Beispiel: uv run python main.py generate-case W1")
            sys.exit(1)
        case_id = args[1]
        model = parse_model(args[2:])
        run_single(case_id, model)

    elif command == "status":
        show_status()

    else:
        print(f"Unbekannter Befehl: '{command}'")
        print()
        print_usage()
        sys.exit(1)


if __name__ == "__main__":
    main()
