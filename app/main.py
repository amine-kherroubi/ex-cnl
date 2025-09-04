from __future__ import annotations
import sys
import argparse
from app.application_facade import ApplicationFacade
from app.utils.exceptions import ApplicationError


def create_argument_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser"""
    parser = argparse.ArgumentParser(
        description="Document generator for BNH (ex-CNL) reports",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m app.main --list                    # List available documents
  python -m app.main --document activite_mensuelle_par_programme
  python -m app.main --document situation_des_programmes --output custom_output.xlsx
  
Note: Required files must be present in the current working directory.
        """,
    )

    parser.add_argument(
        "--list",
        action="store_true",
        help="List all available documents and their required files",
    )

    parser.add_argument(
        "--document", type=str, help="Generate a specific document by name"
    )

    parser.add_argument(
        "--output", type=str, help="Output file path (used with --document)"
    )

    return parser


def validate_arguments(args: argparse.Namespace) -> None:
    """Validate command line arguments"""
    if args.output and not args.document:
        raise ValueError("--output can only be used with --document")

    if not args.list and not args.document:
        raise ValueError("Either --list or --document must be specified")


def main() -> None:
    """Main entry point"""
    parser = create_argument_parser()
    args = parser.parse_args()

    try:
        # Validate arguments
        validate_arguments(args)

        # Create application facade
        app_facade = ApplicationFacade()

        # Execute based on arguments
        if args.list:
            app_facade.list_available_documents()
        elif args.document:
            app_facade.generate_document(args.document, args.output)

        print("✓ Operation completed successfully")
        sys.exit(0)

    except KeyboardInterrupt:
        print("\n⚠ Operation cancelled by user")
        sys.exit(1)

    except FileNotFoundError as e:
        print(f"✗ File error: {e}")
        sys.exit(1)

    except ValueError as e:
        print(f"✗ Invalid argument: {e}")
        print("\nUse --help for usage information")
        sys.exit(1)

    except ApplicationError as e:
        print(f"✗ Application error: {e}")
        sys.exit(1)

    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
