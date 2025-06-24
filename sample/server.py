import submarine_py
import logging


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
        description="submarine game server",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "--host", default='',
        help="hostname or ip address to bind, or '' for all interfaces",
    )
    parser.add_argument(
        "--port", type=int, default=2000,
        help="port number to listen, e.g., 2000",
    )
    parser.add_argument(
        "--games", type=int, default=1,
        help="number of games",
    )
    parser.add_argument(
        "--quiet", action='store_true',
        help="run quietly",
    )
    parser.add_argument(
        "--verbose", action='store_true',
        help="show messages received from or sent to clients",
    )
    parser.add_argument(
        "--field-width", type=int, default=5,
        help="width of field",
    )
    parser.add_argument(
        "--field-height", type=int, default=5,
        help="height of field",
    )
    parser.add_argument(
        "--rounded-field", action='store_true',
        help="configure corners impassablea",
    )
    args = parser.parse_args()
    FORMAT = '%(asctime)s %(levelname)s %(message)s'
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(format=FORMAT, level=log_level, force=True)
    rocks = []
    if args.rounded_field:
        rocks = [
            [x, y]
            for x in [0, args.field_width - 1]
            for y in [0, args.field_height - 1]
        ]
        logging.debug(f'{rocks}')
    field = submarine_py.Field(args.field_height, args.field_width, rocks)
    logging.debug(f'field is\n{field.to_ascii()}')
    submarine_py.server_main(
        args.host, args.port, args.games,
        field,
        quiet=args.quiet
    )
