#! /usr/bin/python3
import argparse
import logging
import ipaddress
import socket
import urllib.request
import cloudflare
import tldextract
from typing import Union, Set

prog = "update-ddns"
version = "0.1"
author = "Carl Edman (CarlEdman@gmail.com)"
desc = "Update, if necessary, the current A record at cloudflare."

parser = None
args = None
log = logging.getLogger()

def get_public_ip_addresses() -> Set[Union[ipaddress.IPv4Address, ipaddress.IPv6Address]]:
  contents = args.ip or urllib.request.urlopen(args.ip_resolver).read()
  ips = [ ipaddress.ip_address(contents.decode('utf-8')) ]
  return set(ips)

def get_dns_ip_addresses() ->  Set[Union[ipaddress.IPv4Address, ipaddress.IPv6Address]]:
  args.names = args.names or [ None ]
  ips = []
  for a in args.names:
    bs = socket.getaddrinfo(a, None, family = socket.AF_INET | socket.AF_INET6)
    for (family, _, _, _, ip) in bs:
      if family in { socket.AF_INET, socket.AF_INET6 }:
        ips.append(ipaddress.ip_address(ip[0].removeprefix('::ffff:')))
  return set(ips)

def update_cloudflare(name : str, ips: Set[Union[ipaddress.IPv4Address, ipaddress.IPv6Address]]):
  tld = tldextract.extract(name)
  sub = tld.subdomain
  if sub == "*":
    sub = "@"
  dom = tld.registered_domain
  log.info(f"Updating {sub or 'base domain'} on cloudflare name server for {dom} to {', '.join(map(str, public_ips))}.")

  # if not args.token:
  #     log.error(
  #         "Cloudflare requires the --ddns-token options to be set.  These can be found at https://dash.cloudflare.com/profile/api-tokens.  Be sure to include the Edit Zone DNS privilege."
  #     )
  token = args.token
  if token and not token.startswith("Bearer "):
    token = "Bearer " + token
  client = cloudflare.Cloudflare(api_email=args.email,
                                 api_key=args.api,
                                 user_service_key=token)

  zone_ids = [ z.id for z in client.zones.list(name=dom) ]
  if len(zone_ids) < 1:
    log.error("No zone ids returned.")
    return
  if len(zone_ids) > 1:
    log.error("Multiple zone ids returned.")
    return
  zone_id = zone_ids[0]
  zone = client.zones.get(zone_id=zone_id)
  for d in client.dns.records.list(zone_id = zone_id):
    print(d)


ddns_providers = {
  "cloudflare": update_cloudflare,
}

if __name__ == "__main__":
  parser = argparse.ArgumentParser(
    fromfile_prefix_chars="@", prog=prog, epilog="Written by: " + author
  )
  parser.add_argument(
    "-f",
    "--force",
    dest="force",
    action="store_true",
    help="force updates even if seemingly unnecessary.",
  )
  parser.add_argument(
    "-d",
    "--ddns-provider",
    action="store",
    default="cloudflare",
    choices=ddns_providers.keys(),
    help="DNS provider whose record to update.",
  )
  parser.add_argument(
    "--ddns-email",
    dest="email",
    action="store",
    help="DNS provider's registered email.",
  )
  parser.add_argument(
    "--ddns-api",
    dest="api",
    action="store",
    help="DNS provider's API key with appropriate permissions.",
  )
  parser.add_argument(
    "--ddns-token",
    dest="token",
    action="store",
    help="DNS provider's user service token.",
  )
  parser.add_argument(
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
    "--log",
     dest = "logfile", 
     action = "store",
     help = "location of alternate log file."
  )
  parser.add_argument(
    "--ip-resolver",
    help = "URL to fetch to get current public IP address.",
    default = "http://ipinfo.io/ip",
  )
  parser.add_argument(
    "--ip", 
    help="New IP address, defaults to current public IP address."
  )
  parser.add_argument(
    "names",
    nargs = "*",
    help="DNS names to be updated.",
  )
  parser.set_defaults(loglevel=logging.WARN)

  args = parser.parse_args()
  if args.dryrun and args.loglevel > logging.INFO:
    args.loglevel = logging.INFO

  logformat = logging.Formatter("%(asctime)s [%(levelname)s]: %(message)s")
  log.setLevel(0)

  if args.logfile:
    flogger = logging.handlers.WatchedFileHandler(args.logfile, "a", "utf-8")
    flogger.setLevel(logging.DEBUG)
    flogger.setFormatter(logformat)
    log.addHandler(flogger)

  slogger = logging.StreamHandler()
  slogger.setLevel(args.loglevel)
  slogger.setFormatter(logformat)
  log.addHandler(slogger)

  public_ips = get_public_ip_addresses()
  log.info(f"Retrieved public IP addresses: {', '.join(map(str, public_ips))}")
  dns_ips = get_dns_ip_addresses()
  log.info(f"Retrieved DNS IP addresses: {', '.join(map(str, dns_ips))}")
  if not args.force and public_ips == dns_ips:
    log.info("Public and DNS IP addresses match, skipping update.")
    exit(0)
  
  updater = ddns_providers[args.ddns_provider]
  for name in args.names:
    updater(name, public_ips)
