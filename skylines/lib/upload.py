from enum import Enum


class UploadStatus(Enum):
    SUCCESS = 0
    DUPLICATE = 1  # _('Duplicate file')
    MISSING_DATE = 2  # _('Date missing in IGC file')
    PARSER_ERROR = 3  # _('Failed to parse file')
    NO_FLIGHT = 4  # _('No flight found in file')
    FLIGHT_IN_FUTURE = 5  # _('Date of flight in future')
