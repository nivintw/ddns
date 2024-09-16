# digital-ocean-dynamic-dns

[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
![coverage badge](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/nivintw/d3939953524d972fa08a6e494be4e12f/raw/pytest-coverage-comment__main.json)
![CI status badge](https://github.com/nivintw/ddns/actions/workflows/python.yaml/badge.svg)

Dynamic DNS python tool for Digital Ocean

This project offers a way to manage dynamic DNS, with specific support for [DigitalOcean](https://www.digitalocean.com/) authoritative DNS servers.

Example:

1. I own the domain `nivin.tech`
1. DigitalOcean is my authoritative name server provider for the `nivin.tech` domain.
1. I use this package (installed as a command line utility and deployed on a device on my home network) to update the DNS records for `nivin.tech` to point at my home gateway, which is assigned a dynamic IP address by my internet service provider (ISP).

## Installation

Recommended installation path is to install this repository using [pipx](https://github.com/pypa/pipx). `pipx` provides the ability to install command line tools like this one into isolated environments, keeping your system-level packages clean and removing the possibility of dependency conflicts across tools.

Another alternative option to `pipx` is the (relatively) new tool [uv](https://github.com/astral-sh/uv). See [this blog post](https://astral.sh/blog/uv-unified-python-packaging) for more information and information on the recent features added to `uv`. If going the uv route, you want `uv tool install`.

## Appendix

This is an appendix of the various terms used in the library.

domain: A domain as described by Digital Ocean (see [here](https://docs.digitalocean.com/products/networking/dns/getting-started/quickstart/)).
This is specifically a "two part" domain such as "example.com" without any sub-domains specified.

subdomain: A subdomain as described by Digital Ocean (see [here](https://docs.digitalocean.com/products/networking/dns/how-to/add-subdomain/)).
This can be any subdomain that Digital Ocean supports.
Subdomains must be associated with a registered and managed domain.

manage (domain context): Refers specifically to having digital-ocean-dynamic-dns catalog the corresponding domain.
Domains must be managed by digital-ocean-dynamic-dns in order to manage corresponding subdomains.

manage (subdomain context): Refers specifically to having digital-ocean-dynamic-dns handle updating the IP address associated with the corresponding subdomain.

un-manage (domain context): Mark the corresponding domain as un-managed in the digital-ocean-dynamic-dns local database/catalog.
This will have the effect of un-managing (but not de-registering nor remove) the corresponding subdomains.

un-manage (subdomain context): Mark the corresponding subdomain as un-managed in the digital-ocean-dynamic-dns local database/catalog.
This will result in the IP address no longer being managed by digital-ocean-dynamic-dns.
This does not remove the entry for the subdomain from the local digital-ocean-dynamic-dns database/catalog.
This will not de-register the associated subdomain.

remove (domain context): Removes the associated domain from the digital-ocean-dynamic-dns local database/catalog.
This has the additional effect of removing corresponding subdomains.
No de-register actions are taken as part of a remove action; changes are to the digital-ocean-dynamic-dns local database/catalog only.

remove (subdomain context): Removes the associated subdomain from the digital-ocean-dynamic-dns local database/catalog.
No de-register actions are taken as part of a remove action; changes are to the digital-ocean-dynamic-dns local database/catalog only.

catalog: Store an entry in the digital-ocean-dynamic-dns database for the corresponding domain or subdomain.
Domains and subdomains can be cataloged and not managed.

register (subdomain context): Make changes to you Digital Ocean account to add the corresponding subdomain record to the corresponding Domain registration.
This requires that the top domain (e.g. example.com for subdomain my.example.com) be both registered and managed.

deregister (subdomain context): Make changes to your Digital Ocean account to remove the corresponding subdomain records from the corresponding Domain registration.
This has the additional effect of removing the subdomain from the local digital-ocean-dynamic-dns database.

## Planned Updates

- [ ] Add support for multiple IP address resolvers.
  - examples: https://ip-api.com, https://api.whatismyip.com/ip.php?key=<API_KEY>, etc
- [ ] Finish updating the command line user interface.
  - Substantial changes have already been made, and further re-writes are planned.
  - [/] changes to using subparsers instead of overloaded command line flags.
  - [/] Revise language to be more clear about what is being managed and how.
  - [ ] substantial changes to argparse usage/implementation
- [ ] Update README.md to highlight where/how this tool is intended to be used.
- [ ] Update logging features/implementation.
- [ ] Register and upload package to PyPI.
- [ ] Add automated CI/CD process including package release to PyPI.
- [ ] Integrate python-semantic-release for version management.
- [ ] Add support for purging local database (without updating DO records).
  - Used to just get a "fresh install".
- [ ] Add support to read config from a toml file.
