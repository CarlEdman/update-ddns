#! python
import argparse
import logging
import socket

prog = "update-cloudflare"
version = "0.1"
author = "Carl Edman (CarlEdman@gmail.com)"
desc = "Update, if necessary, the current A record at cloudflare."

parser = None
args = None
log = logging.getLogger()



if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        fromfile_prefix_chars="@", prog=prog, epilog="Written by: " + author
    )
    # parser.add_argument(
    #     "-n",
    #     "--no-delete",
    #     dest="nodelete",
    #     action="store_true",
    #     help="do not delete source files (e.g., video, subtitles, or posters) after conversion to MKV.",
    # )
    # parser.add_argument(
    #     "-t",
    #     "--title-case",
    #     dest="titlecase",
    #     action="store_true",
    #     help="rename files to proper title case.",
    # )
    # parser.add_argument(
    #     "-f",
    #     "--force",
    #     dest="force",
    #     action="store_true",
    #     help="force remuxing without any apparent need.",
    # )
    # parser.add_argument(
    #     "-l",
    #     "--languages",
    #     dest="languages",
    #     action="store",
    #     help="keep audio and subtitle tracks in the given language ISO639-2 codes; prefix with ! to discard same.",
    # )
    # parser.add_argument(
    #     "--default-language",
    #     dest="default_language",
    #     action="store",
    #     default="eng",
    #     choices=iso6392tolang.keys(),
    #     help="ISO6392 language code to use by default for subtitles.",
    # )
    parser.add_argument(
        "-d",
        "--dryrun",
        dest="dryrun",
        action="store_true",
        help="do not perform operations, but only print them.",
    )
    parser.add_argument("--version", action="version", version="%(prog)s " + version)
    parser.add_argument(
        "--verbose",
        dest="loglevel",
        action="store_const",
        const=logging.INFO,
        help="print informational (or higher) log messages.",
    )
    parser.add_argument(
        "--debug",
        dest="loglevel",
        action="store_const",
        const=logging.DEBUG,
        help="print debugging (or higher) log messages.",
    )
    parser.add_argument(
        "--taciturn",
        dest="loglevel",
        action="store_const",
        const=logging.ERROR,
        help="only print error level (or higher) log messages.",
    )
    parser.add_argument(
        "--log", dest="logfile", action="store", help="location of alternate log file."
    )
    parser.add_argument(
        "--name-resolver",
        help="URL to fetch to get current public IP address.",
        default="http://ipinfo.io/ip",
    )
    parser.add_argument(
        "name",
        help="DNS name to be updated.",
    )
    parser.add_argument(
        "ip",
        help="New IP address, defaults to public IP address."
    )
    parser.set_defaults(loglevel=logging.WARN)

    args = parser.parse_args()
    if args.dryrun and args.loglevel > logging.INFO:
        args.loglevel = logging.INFO

    log.setLevel(0)
    logformat = logging.Formatter("%(asctime)s [%(levelname)s]: %(message)s")

    if args.logfile:
        flogger = logging.handlers.WatchedFileHandler(args.logfile, "a", "utf-8")
        flogger.setLevel(logging.DEBUG)
        flogger.setFormatter(logformat)
        log.addHandler(flogger)

    slogger = logging.StreamHandler()
    slogger.setLevel(args.loglevel)
    slogger.setFormatter(logformat)
    log.addHandler(slogger)

