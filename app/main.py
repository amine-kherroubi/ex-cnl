from __future__ import annotations

# Standard library imports
import sys
import argparse
from pathlib import Path
from typing import Final

# Local application imports
from app.application_facade import ApplicationFacade
from app.utils.exceptions import ApplicationError
from app.config import AppConfig
from app.utils.logging_setup import LoggingSetup, get_logger


def create_argument_parser() -> argparse.ArgumentParser:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        prog="python -m app.main",
        description="Document generator for BNH (ex-CNL) reports",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  %(prog)s --list\n"
            "  %(prog)s --document activite_mensuelle_par_programme\n"
            "  %(prog)s --document situation_des_programmes --output report.xlsx\n"
            "  %(prog)s --document monthly_stats --output /path/to/output.xlsx\n"
            "\n"
            "Note: Input files must be present in the current working directory.\n"
            "      Use --list to see required files for each document type."
        ),
        allow_abbrev=True,
    )

    main_action = parser.add_mutually_exclusive_group(required=True)
    main_action.add_argument(
        "--list",
        action="store_true",
        help="list all available documents and their required input files",
    )
    main_action.add_argument(
        "--document",
        type=str,
        metavar="NAME",
        help="generate a specific document by name (use --list to see options)",
    )

    parser.add_argument(
        "--output",
        type=Path,
        metavar="FILE",
        help="output file path (optional, auto-generated if not specified)",
    )
    parser.add_argument(
        "--version", action="version", version="BNH Document Generator 1.0.0"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="show what would be done without actually generating files",
    )
    parser.add_argument(
        "--force",
        "-f",
        action="store_true",
        help="overwrite existing output files without prompting",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="enable debug logging output",
    )
    parser.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        help="reduce output verbosity (WARNING level and above only)",
    )

    return parser


def validate_arguments(args: argparse.Namespace) -> None:
    if args.output:
        if not args.output.suffix:
            raise ValueError(
                f"Output file must have an extension: {args.output}\n"
                "Supported formats: .xlsx, .pdf, .docx, .csv"
            )

        valid_extensions: Final[set[str]] = {
            ".xlsx",
            ".pdf",
            ".docx",
            ".csv",
            ".json",
            ".txt",
        }
        if args.output.suffix.lower() not in valid_extensions:
            raise ValueError(
                f"Unsupported file extension: {args.output.suffix}\n"
                f"Supported extensions: {', '.join(sorted(valid_extensions))}"
            )

        parent_dir: Final[Path] = args.output.parent
        if not parent_dir.exists():
            raise FileNotFoundError(
                f"Output directory does not exist: {parent_dir}\n"
                "Create the directory or choose a different path"
            )
        if not parent_dir.is_dir():
            raise ValueError(f"Parent path is not a directory: {parent_dir}")
        if not parent_dir.stat().st_mode & 0o200:
            raise PermissionError(f"No write permission for directory: {parent_dir}")
        if args.output.exists() and not args.force and not args.dry_run:
            raise ValueError(
                f"Output file already exists: {args.output}\n"
                "Use --force to overwrite or choose a different path"
            )

    if args.document and len(args.document) > 100:
        raise ValueError(
            f"Document name too long: {len(args.document)} characters\n"
            "Maximum length is 100 characters"
        )


def setup_logging(config: AppConfig, args: argparse.Namespace) -> None:
    if args.debug:
        config.logging_config.level = "DEBUG"
        config.logging_config.console_level = "DEBUG"
    elif args.quiet:
        config.logging_config.console_level = "WARNING"

    LoggingSetup.configure(config.logging_config)


def main() -> None:
    try:
        parser: argparse.ArgumentParser = create_argument_parser()
        args: argparse.Namespace = parser.parse_args()

        # Load configuration
        config: AppConfig = AppConfig()

        # Setup logging early
        setup_logging(config, args)

        # Get logger after logging is configured
        logger = get_logger("app.main")
        logger.info("Application starting up")
        logger.debug(f"Command line arguments: {vars(args)}")

        validate_arguments(args)

        app: ApplicationFacade = ApplicationFacade(config=config)
        logger.debug("ApplicationFacade initialized")

        if args.list:
            logger.info("Listing available documents")
            print("Available documents:")
            print("-" * 60)
            for (
                doc_name,
                document_specification,
            ) in app.get_available_documents().items():
                print(f"• {document_specification.display_name}")
                print(f"  Name: {doc_name}")
                print(f"  Category: {document_specification.category}")
                print(f"  Description: {document_specification.description}")
                print(f"  Required files (patterns):")
                for pattern in document_specification.required_files:
                    print(f"    - {pattern}")
                print()
            logger.info(
                f"Listed {len(app.get_available_documents())} available documents"
            )

        elif args.document:
            logger.info(f"Processing document generation request: {args.document}")

            if args.dry_run:
                logger.info("Running in dry-run mode")
                print(f"🔍 Dry run mode: Would generate document '{args.document}'")
                if args.output:
                    print(f"🔍 Output would be saved to: {args.output}")
                else:
                    print("🔍 Output would use default naming")
                print("✅ Dry run completed - no files were modified")
                logger.info("Dry run completed successfully")
            else:
                logger.info(f"Generating document: {args.document}")
                if args.output:
                    logger.debug(f"Output path specified: {args.output}")

                app.generate_document(args.document, args.output)
                print(f"✅ Document '{args.document}' generated successfully")
                logger.info(f"Document '{args.document}' generated successfully")

        logger.info("Application completed successfully")
        sys.exit(0)

    except KeyboardInterrupt:
        logger = get_logger("app.main")
        logger.warning("Operation cancelled by user")
        print("\n⚠️  Operation cancelled by user", file=sys.stderr)
        sys.exit(130)

    except FileNotFoundError as error:
        logger = get_logger("app.main")
        logger.error(f"File not found: {error}")
        print(f"❌ File error: {error}", file=sys.stderr)
        print("\n💡 Troubleshooting:", file=sys.stderr)
        print("   • Check that all required input files exist", file=sys.stderr)
        print("   • Verify file paths and permissions", file=sys.stderr)
        print(
            "   • Use --list to see required files for each document", file=sys.stderr
        )
        sys.exit(2)

    except ValueError as error:
        logger = get_logger("app.main")
        logger.error(f"Invalid usage: {error}")
        print(f"❌ Invalid usage: {error}", file=sys.stderr)
        print("\n💡 Use --help for detailed usage information", file=sys.stderr)
        sys.exit(2)

    except PermissionError as error:
        logger = get_logger("app.main")
        logger.error(f"Permission error: {error}")
        print(f"❌ Permission error: {error}", file=sys.stderr)
        print("\n💡 Check file/directory permissions and try again", file=sys.stderr)
        sys.exit(13)

    except ApplicationError as error:
        logger = get_logger("app.main")
        logger.error(f"Application error: {error}")
        print(f"❌ Application error: {error}", file=sys.stderr)
        print("\n💡 Check your input data and configuration", file=sys.stderr)
        sys.exit(3)

    except Exception as error:
        logger = get_logger("app.main")
        logger.exception("Unexpected error occurred")  # This logs the full traceback
        print(f"❌ Unexpected error: {error}", file=sys.stderr)
        print("\n🔍 Debug information:", file=sys.stderr)
        import traceback

        traceback.print_exc()
        print(
            "\n💡 This appears to be a bug. Please report it with the above details.",
            file=sys.stderr,
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
