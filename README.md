# ddns_digital_ocean

Dynamic DNS python tool for Digital Ocean  
This is a fork of https://gitlab.pm/rune/ddns.
Note: As of August 4th, 2024, the original repository is not accessible from the U.S.

Mainly focusing on bug fixes and my own personal use.

This project offers a way to manage dynamic DNS, with specific support for [DigitalOcean](https://www.digitalocean.com/) authoritative DNS servers.

Example:

1. I own the domain `nivin.tech`
1. DigitalOcean is my authoritative name server provider for the `nivin.tech` domain.
1. I use this package (installed as a command line utility and deployed on a device on my home network) to update the DNS records for `nivin.tech` to point at my home gateway, which is assigned a dynamic IP address by my internet service provider (ISP).

## Installation

Recommended installation path is to install this repository using [pipx](https://github.com/pypa/pipx). `pipx` provides the ability to install command line tools like this one into isolated environments, keeping your system-level packages clean and removing the possibility of dependency conflicts across tools.

Another alternative option to `pipx` is the (relatively) new tool [uv](https://github.com/astral-sh/uv). See [this blog post](https://astral.sh/blog/uv-unified-python-packaging) for more information and information on the recent features added to `uv`. If going the uv route, you want `uv tool install`.

## Planned Updates

- [ ] Finish updating the command line user interface.
  - Substantial changes have already been made, and further re-writes are planned.
  - [/] changes to using subparsers instead of overloaded command line flags.
  - [/] Revise language to be more clear about what is being managed and how.
  - [ ] substantial changes to argparse usage/implementation
- [ ] rename package to digital-ocean-dynamic-dns
- [ ] Update README.md to highlight where/how this tool is intended to be used.
- [ ] Update logging features/implementation.
- [/] Create tests for the codebase and reach > 80% coverage.
- [ ] Add support for reading the Digital Ocean API key from environment variables.
  - Environment variables will have precedence over stored api key.
- [ ] Rename and update sub-domain related management functions.
- [ ] Register and upload package to PyPI.
- [ ] Add automated CI/CD process including package release to PyPI.
- [ ] Integrate python-semantic-release for version management.
- [ ] Change license to MIT license
  - This will happen when this codebase undergoes further revision and reaches an "inspired by" state.
  - Currently, substantial changes have been made from the original fork. With other planned changes, most of the original code will no longer be part of this project.
