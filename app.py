import sys
import ria_parser
import tass_parser
import rbc_parser
import datetime
import log as Logger

ARGV_PARAM_TAGS = 1
ARGV_START_DATE = 2
ARGV_END_DATE = 3
ARGV_PARSER_CODE = 4

log = Logger.get_logger(__name__)


def execute():
    try:
        if len(sys.argv) >= 3 and len(sys.argv) <= 5:
            params = sys.argv[ARGV_PARAM_TAGS]
            start_date = sys.argv[ARGV_START_DATE]
            parser_code = 0
            end_date = datetime.datetime.now().strftime('%d/%m/%Y')
            if len(sys.argv) == 4:
                end_date = sys.argv[ARGV_END_DATE]
            else:
                end_date = sys.argv[ARGV_END_DATE]
                _pv = sys.argv[ARGV_PARSER_CODE]
                parser_code = _pv if _pv < 4 and _pv >= 0 else 0

            for func in parsers.get(parser_code):
                func(params, start_date, end_date)
            sys.stdout.write('Script finished check output files')
        else:
            log.info("Incorrect params = " + repr(sys.argv))
            sys.stdout.write('Incorrect params check github repository')
    except:
        log.exception('Input params = ' + repr(sys.argv))
        sys.stderr.write('Something go wrong open. Check logs.\n')


parsers = {
    1: [ria_parser.start_request],
    2: [tass_parser.start_request],
    3: [rbc_parser.start_request],
    0: [ria_parser.start_request, tass_parser.start_request, rbc_parser.start_request]
}


if __name__ == "__main__":
    execute()
