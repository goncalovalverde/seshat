import pandas as pd
import logging

# Constants
FORMAT_XLSX = "xlsx"
FORMAT_CSV = "csv"
FORMAT_KEY = "format"
FILENAME_KEY = "filename"

def write_data(data: pd.DataFrame, config: dict) -> None:
    """Writes the provided data to a file in the specified format."""
    format = config.get(FORMAT_KEY)
    filename = config.get(FILENAME_KEY)

    if format == FORMAT_XLSX:
        logging.debug("Writing cycle_data to excel file %s", filename)
        with pd.ExcelWriter(filename) as writer:
            data.to_excel(writer)
    elif format == FORMAT_CSV:
        logging.debug("Writing cycle_data to csv file %s", filename)
        data.to_csv(filename, index=False)
    else:
        raise ValueError(f"Unsupported format: {format}")

def export_csv(data: pd.DataFrame, filename: str) -> None:
    """Exports the provided data to a CSV file."""
    logging.debug("Exporting data to csv file %s", filename)
    data.to_csv(filename, index=False)