# DDNS

_DDNS_ is a dynamic DNS helper for Digital Ocean users to utilize their DO account as a Dynamic DNS resolver.

## Installation

Download the latest relase from https://gitlab.pm/rune/ddns/releases. Unzip and move to a folder in you path (ease of use). You can also rename the file ```ddns.py``` to just ```ddns``` and make the file executable with ```chmod +x ddns```. To install required python modules run ```pip3 install -r requirements.txt```

## Usage

For instructions run

```bash
ddns -h
```

The program is best suited to be executed with e.g cron or any other system that can run at intervals. To run the app every 6 hours with cron add the following line to your crontab

```bash
0 */6 * * *  /usr/local/bin/ddns
```

## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

## Support

If you found a bug or you have suggestion for new features create an issue.

## Future development

- [ ] IPv6 support
- [ ] Add and delete non existing (new) domains to DO account

## License

[<img src="https://www.gnu.org/graphics/gplv3-with-text-136x68.png">](https://www.gnu.org/licenses/gpl-3.0.en.html)
