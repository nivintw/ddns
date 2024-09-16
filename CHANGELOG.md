# CHANGELOG

## v0.1.0 (2024-09-16)

### Feature

* feat(ci): :construction_worker: Add semantic-release to CI workflow

Should enable semantic-release to be run on the main branch from now on ([`a3def05`](https://github.com/nivintw/ddns/commit/a3def05258a4eef688d435687edfe882bc4104ef))

### Refactor

* refactor: clean up args.py ([`484557a`](https://github.com/nivintw/ddns/commit/484557a12842a8534d37729453ecbc112784319e))

* refactor: update UX related to domains management. ([`170e4e3`](https://github.com/nivintw/ddns/commit/170e4e3eaa404b128c20f39bb8718ccaa96d478b))

* refactor: add logs subparser ([`2c43db5`](https://github.com/nivintw/ddns/commit/2c43db535d5b2a5e1dc9b19d8350108de9487553))

* refactor: add early returns when there are no dynamic domains active.

NOTE: the code actually looks for a subdomain to be configured...
check relationship between subdomain and domain and if this is how this should behave. ([`cfd0187`](https://github.com/nivintw/ddns/commit/cfd0187f8f5bb16acfdcd35f19a26db0668dc1dc))

* refactor: ensure transaction is automatically committed or rolled back.

connection context manager for api_key_helpers.py ([`2f7f687`](https://github.com/nivintw/ddns/commit/2f7f68785c11ba6b655816efb74d4c60fae16f62))

* refactor: change how the big line of &#39;=&#39; is printed.

use &#39;=&#39; * 114 instead of putting 114 &#39;=&#39; chars in the code. ([`5bb3c5d`](https://github.com/nivintw/ddns/commit/5bb3c5dc68efc6731b1f755bba15a4a47fcc6671))

### Unknown

* Merge pull request #5 from nivintw/add-python-semantic-release

feat(ci): :construction_worker: Add semantic-release to CI workflow ([`0785e48`](https://github.com/nivintw/ddns/commit/0785e48d38f21bf6ed1337c7368762f94adfd576))

* add checkout back to tests ([`c081bfd`](https://github.com/nivintw/ddns/commit/c081bfdb4db217a6b59a829afe2a7ed0018a983e))

* coverage badge links to workflow ([`f2f9bdf`](https://github.com/nivintw/ddns/commit/f2f9bdf20e57656aec1a5768e173559351779280))

* Update CI / Test status badge ([`0d5319e`](https://github.com/nivintw/ddns/commit/0d5319e51c7b89b6356f55e04d5454a0878eb3ae))

* add pre-commit ([`1a3f604`](https://github.com/nivintw/ddns/commit/1a3f60481149079c04babb4d75a7cedcc18b2504))

* add ruff badge
restrict generating coverage badge updates to default branch ([`02afceb`](https://github.com/nivintw/ddns/commit/02afceb3f7622fe893f5d859925ffea3ed553b97))

* add CI status badge ([`e46c289`](https://github.com/nivintw/ddns/commit/e46c28948a79320dc2d12dacf5d075559855d023))

* add coverage badge via gist ([`f099c41`](https://github.com/nivintw/ddns/commit/f099c41ea2126f42eacea1c2154a8e037b81b28a))

* clean up accidentally added file ([`d19f46b`](https://github.com/nivintw/ddns/commit/d19f46b79b45ae394375c55b7ffbcb4e8253610e))

* stahppp ([`4a3f85b`](https://github.com/nivintw/ddns/commit/4a3f85b2a58e91b40a2591eea572abb026b843ff))

* Update coverage on Readme ([`6bf3508`](https://github.com/nivintw/ddns/commit/6bf35088a6519a7686ac2f9b68779d5201ebc189))

* Update coverage on Readme ([`3072808`](https://github.com/nivintw/ddns/commit/3072808115d4b45e788587b99d4214f41e6a61dc))

* Update coverage on Readme ([`01cd6dd`](https://github.com/nivintw/ddns/commit/01cd6dd773555e99a3b99e1ddbe096e1e6e86a29))

* Update coverage on Readme ([`143f9fb`](https://github.com/nivintw/ddns/commit/143f9fbadf7e602d3e0e7375755d7cd4106e7d59))

* Update coverage on Readme ([`cd04f71`](https://github.com/nivintw/ddns/commit/cd04f717af398dc3820028187cd79d927a24a1fb))

* Update coverage on Readme ([`18338d3`](https://github.com/nivintw/ddns/commit/18338d3e4b5ce7e002277ac3b3786e2ef0cb0b32))

* Update coverage on Readme ([`e8e4363`](https://github.com/nivintw/ddns/commit/e8e436387bf2a4627c8fe306c62216ef555c6f2d))

* Update coverage on Readme ([`4c2c767`](https://github.com/nivintw/ddns/commit/4c2c7670dfe5e142de1c3501f5855d2e22c955a3))

* Merge pull request #4 from nivintw/fix_workflow_auth

try fixing auth ([`95a8be2`](https://github.com/nivintw/ddns/commit/95a8be22e58780caff3fe6023f0d655b0882fec3))

* try fixing auth ([`06287ab`](https://github.com/nivintw/ddns/commit/06287ab047c5c52f99320ff7dc4528254c534669))

* Merge pull request #3 from nivintw/update_workflow

try updating creds used for updating readme.me ([`4fe653c`](https://github.com/nivintw/ddns/commit/4fe653c68cedbd37c301aed7b7cc8a548bb3555c))

* try updating creds used for updating readme.me ([`72fc5c9`](https://github.com/nivintw/ddns/commit/72fc5c93d87cec326edf46d1d8f79f0130b7b91b))

* Merge pull request #2 from nivintw/update_readme_automatically

Update readme automatically ([`3228d69`](https://github.com/nivintw/ddns/commit/3228d69072818342111988239d83c894f6fd99ba))

* update if ([`1c336c7`](https://github.com/nivintw/ddns/commit/1c336c7ddbda23f3b1bfa8b65089859613f65a33))

* main has to be hard-coded turns out ([`edd7247`](https://github.com/nivintw/ddns/commit/edd724776c59021c84943c1c1bdecd0dc929c0c3))

* Merge pull request #1 from nivintw/add_ci

Add ci ([`c60c5ed`](https://github.com/nivintw/ddns/commit/c60c5ed6ddb62a80525bc6db78e9803d7e12775f))

* add pytest coverage badge to readme.md ([`99b955b`](https://github.com/nivintw/ddns/commit/99b955be46bf34608826924d28c6c854914e0047))

* rename ([`c70008e`](https://github.com/nivintw/ddns/commit/c70008e5ae6ef87386ddfe23ba1044f6870b93a3))

* remove unneeded steps ([`bf15b5e`](https://github.com/nivintw/ddns/commit/bf15b5efbac7149533f9c61e9317d6d85d35aa08))

* tweak to see if output is wrong with txt output ([`d8ad1a4`](https://github.com/nivintw/ddns/commit/d8ad1a4fe66cbadd2911d3b09164dbc40d0f2136))

* add pytest-coverage-comment ([`6436ece`](https://github.com/nivintw/ddns/commit/6436eced7849873ed2857ac9ab47690163863bfc))

* grant permission to write pull-requests to allow commenting to work ([`32d5de7`](https://github.com/nivintw/ddns/commit/32d5de7ef9ff7f9e7c40a969dca51f797768d4a9))

* fix typo ([`b1562cb`](https://github.com/nivintw/ddns/commit/b1562cb9e700c8c621b229412fdeef67ac89cfd9))

* test adding test summary results as comment on PR ([`ff47d23`](https://github.com/nivintw/ddns/commit/ff47d237d03f30a7d0bb85334b370692ee41fe49))

* tweak to Test Summary ([`78e9b20`](https://github.com/nivintw/ddns/commit/78e9b200d40f1b8d6c7226730076f38565061a02))

* more tweak to test-summary ([`0e07703`](https://github.com/nivintw/ddns/commit/0e07703db87650ab38d040d8f6163d5246dff2f2))

* try again ([`9bfdf92`](https://github.com/nivintw/ddns/commit/9bfdf92e0d885283def14e760310913214407210))

* update test-summary output ([`11e7eff`](https://github.com/nivintw/ddns/commit/11e7eff74cb099c95b32cc0c494390fbcebc61a0))

* add summary ([`d45d244`](https://github.com/nivintw/ddns/commit/d45d2441dddca17f009a17ebc37e5eed81773a55))

* add publish test results ([`9103b82`](https://github.com/nivintw/ddns/commit/9103b826a230b73251647763f35e0c25e7173795))

* try to add pytest ([`34b12ce`](https://github.com/nivintw/ddns/commit/34b12ceff70df39257596f6c77e62cb2deb1ed89))

* add pre-commit workflow ([`0a4713e`](https://github.com/nivintw/ddns/commit/0a4713efc6a220b8837bbb76dc7873e333a5e9cd))

* update scratch.md ([`46f110e`](https://github.com/nivintw/ddns/commit/46f110e21c61f767bbf934eec63306ab92bffc21))

* vbump ([`fe99d2d`](https://github.com/nivintw/ddns/commit/fe99d2de7ef8ef541c348a7358a89926866a2cd5))

* update license metadata ([`0909d34`](https://github.com/nivintw/ddns/commit/0909d3448ac8948abf79497f818d97a9fc28fc5a))

* update README.md ([`f3cc280`](https://github.com/nivintw/ddns/commit/f3cc2801797320d43232ff2241599074ed4ecc6a))

* minor description update ([`3a092a8`](https://github.com/nivintw/ddns/commit/3a092a8ae752a49c7d18ef0ee500929c9fafebeb))

* package rename ([`d92674c`](https://github.com/nivintw/ddns/commit/d92674c508ca4e69e55b885a146c9262cbbbf496))

* refactor (args.py): several updates.

- remove domains subparser.
  - migrate the list domains functionality to `show_info domains`
- cleanup `-` vs  `_`: use `-` for all sub-parser names.
- remove domains.main wrapper function.
  - not needed anymore.
- Use `test_args.func(test_args)` pattern in tests.
  - This ensures that the parser is configured properly in our tests. ([`a4b2bc3`](https://github.com/nivintw/ddns/commit/a4b2bc31b98562e3de99cb7f80640ac89110c104))

* refactor (show_info): refactor show_info subparser ([`5405c18`](https://github.com/nivintw/ddns/commit/5405c18cbe9cd102008541866eac774dd3a5dc83))

* fix (list_sub_domains): fix output.

Output now correctly handles unmanaged subdomains that exist in the database.
Previously, if a subdomain was in the local DB it was treated as if it was managed, even if it wasn&#39;t managed.
As a result, both 1) cataloged and unmanaged subdomains and 2) uncataloged subdomains (i.e. A records associated with the domain with no corresponding entries in the DB) are treated the same. ([`d2fef27`](https://github.com/nivintw/ddns/commit/d2fef27e289f8e099f356e4a9c711593fe1dde67))

* refactor (subdomains):

- update_all_managed_subdomains looks for managed = 1
- rename NoConfiguredSubdomainsError -&gt; NoManagedSubdomainsError.
- update last_checked and last_updated when re-managing a previously managed subdomain.
- refactor test_no_currently_managed_subdomains. ([`5036068`](https://github.com/nivintw/ddns/commit/5036068bc2ab28b9a9796549d0dcd8536930e7f1))

* feature (manage_subdomain): Update the A record when we claim management of an existing A record. ([`d360415`](https://github.com/nivintw/ddns/commit/d3604155f1a33e4fed3890fae3354dc5f09a19e3))

* feature (un_manage_domain): Implement un_manage_domain. ([`1637674`](https://github.com/nivintw/ddns/commit/1637674b5bbc6f5dcd6845c0d60310f7262953ce))

* feature (un-manage): Add un-manage features.

- Add un-manage subparser.
- Add --list support for un-manage subparser.
- Add domain-level and subdomain-specific un-manage capability.
- Add un_manage_subdomain.
- Add tests for un_manage_subdomain.

TODO: Implement domain-level un-manage capability. ([`98b43c5`](https://github.com/nivintw/ddns/commit/98b43c5a91ac80fee0cadca9879fad850caf3d09))

* build (pre-commit): Update when hawkeye runs.
This will prevent hawkeye and other hooks from fighting each other. ([`d3ea379`](https://github.com/nivintw/ddns/commit/d3ea379c4d8200fc05dba4b404b5316b4293b39e))

* refactor (subdomains.py): refactor list_sub_domains.

- Add tests for list_subdomains.
- Update list_sub_domains to show both managed and un-managed A records for the top domain. ([`5fa1b4c`](https://github.com/nivintw/ddns/commit/5fa1b4c5c7d36284a859972718735b2c07f0c34a))

* tests (TestGetARecordsByName): Add TestGetARecordsByName. ([`35e2d05`](https://github.com/nivintw/ddns/commit/35e2d05bd62a843c4cb8290204457008724c67d0))

* tests (domains.py): add test_manage_all_existing_A_records ([`d6d7f00`](https://github.com/nivintw/ddns/commit/d6d7f005a909d8e4ea74b82c1aad5fefc861167d))

* tests (manage_subdomain): Add test for claiming an name-matching A record. ([`f66913e`](https://github.com/nivintw/ddns/commit/f66913ecbe6aa545d5a3174b14534cae533d10a9))

* tests (subdomains): Update tests for the new get_A_record_by_name call that we make. ([`5865348`](https://github.com/nivintw/ddns/commit/5865348732a27712f4cb83bd1abca03118eba9c1))

* feature (get_A_record_by_name): reclaim A records that match for domain and name fields.

TODO: add tests for get_A_record_by_name. ([`ba95ae2`](https://github.com/nivintw/ddns/commit/ba95ae2ec445b7f5650080aa114c89d05f582d3b))

* comment out purge_database...

decide later if I want to implement this after all. ([`bef3712`](https://github.com/nivintw/ddns/commit/bef3712029ecee03e3cda64dc00117453e2b3dcb))

* tests (env vars): add clear_local_env_var_for_test.

Ensure host-local env vars don&#39;t pollute/manipulate test behavior. ([`13249d3`](https://github.com/nivintw/ddns/commit/13249d3258465e08ba4a3f34e3b6f36180f21399))

* remove note about old location ([`10d5c46`](https://github.com/nivintw/ddns/commit/10d5c468c9ece28130b69d83e8af19f00d91bbb3))

* feature (config): Add support for XDG_DATA_HOME and default user-specific data dirs for mac and linux.

Temporarily un-support windows.
- Windows support added back once I figure out the Windows user-specific data dirs... this shouldn&#39;t be hard, I just never dev on windows. ([`8bcd2ce`](https://github.com/nivintw/ddns/commit/8bcd2ce261c2e88eefcd5c4771a6f2a5d97c78c5))

* add ipython to --dev deps ([`555fef2`](https://github.com/nivintw/ddns/commit/555fef29137dcc053a89e3fcc375a9f3dbc9c247))

* remove deprecated code ([`617c032`](https://github.com/nivintw/ddns/commit/617c032b4390a7cc4464b4e544b5bb05104137e0))

* update readme.md ([`bbef64a`](https://github.com/nivintw/ddns/commit/bbef64aec534fea761c675b5ccb2e02015ef4476))

* feature (api_key_helpers): Support loading DO API Token from DIGITALOCEAN_TOKEN ([`3aa2196`](https://github.com/nivintw/ddns/commit/3aa2196665dd218cff25c2b8a9c6c86a82623caf))

* remove deprecated code ([`6222f22`](https://github.com/nivintw/ddns/commit/6222f22aa4720b2b3e938d882b271909f22e351a))

* refactor (subdomains): refactor list_sub_domains.

This functions lists the managed subdomains for the provided domain. ([`8e9155a`](https://github.com/nivintw/ddns/commit/8e9155a6ca9cfc2926c7229e1a746e9a554b34cd))

* feature (manage.py): add support.

Add support for manage.py and it&#39;s interface.
Add tests for manage.py ([`891b80a`](https://github.com/nivintw/ddns/commit/891b80afb879e5c01e876ca8e3a1df88c980a13e))

* Remove second launch...

This was working, but suddenly stopped... ([`0083817`](https://github.com/nivintw/ddns/commit/00838178cfae8904134c80abd4e0a5597dd26333))

* refactor (exceptions.py): add exceptions.py

move location of exception definition to central location so it can be re-used. ([`92f937d`](https://github.com/nivintw/ddns/commit/92f937d153a060818003a69e4d1aa12886915a34))

* add TODO ([`590ffab`](https://github.com/nivintw/ddns/commit/590ffabf93c6221c4d445419909dcd42f5a1f107))

* add NonSimpleDomainNameError. ([`9802a11`](https://github.com/nivintw/ddns/commit/9802a11bf505cc587f7cee38cff09118b7ba5fe8))

* refactor (update_all_managed_subdomains): move from ip.py to subdomains.py.

This functionality makes more sense in subdomains.py ([`5b6862f`](https://github.com/nivintw/ddns/commit/5b6862ff40939c60b74102aed5d3b6a59a76d17b))

* refactor (updateip): major refactor.

- rename updateip -&gt; update_all_managed_subdomains.
- Completely refactor and review update_all_managed_subdomains.
- add tests for update_all_managed_subdomains. ([`e70f601`](https://github.com/nivintw/ddns/commit/e70f6018a214adf341cc9fad91c0b8d4d2bb30fa))

* add tool.ruff.lint.isort config placeholder. ([`85d48ff`](https://github.com/nivintw/ddns/commit/85d48ffd2a21fbfe373438ed77094a5e0be3eeda))

* feature (do_api.py): Add get_A_record and update_A_record functions. ([`c2b46a3`](https://github.com/nivintw/ddns/commit/c2b46a36c0b46fe9a48519af4277a6cd4b938882))

* tests (create_A_record): add tests for create_A_record. ([`a3efda6`](https://github.com/nivintw/ddns/commit/a3efda69afb515df91ff445a602ceda13a62d4ba))

* add pytest-cov support ([`933e920`](https://github.com/nivintw/ddns/commit/933e9201602681be702b5b6d152c0a8ee96d86b6))

* refactor (ip.py)

major refactor of many functions in ip.py.
Add tests for ip.py functions. ([`4906230`](https://github.com/nivintw/ddns/commit/4906230af8417bf52485b4761e9281a2acb0f759))

* update database schema ([`90585b4`](https://github.com/nivintw/ddns/commit/90585b4682ce79c4b5d0427ae9b33962b70f9b16))

* add  test stubs for get_ip(). ([`fcc14e0`](https://github.com/nivintw/ddns/commit/fcc14e0fc43c212123ebfb7a7da146f838ccd125))

* fix license header template ([`7d3e92e`](https://github.com/nivintw/ddns/commit/7d3e92e1a66fefba2a5bed43fd7de26ad541bd65))

* add tests stub file ([`aa87359`](https://github.com/nivintw/ddns/commit/aa873594aae5d13c37f31c02a394712c84a56644))

* WIP ([`fd4e695`](https://github.com/nivintw/ddns/commit/fd4e695fdb13016c51ceab9034290b0cc268b597))

* update license ([`09c1999`](https://github.com/nivintw/ddns/commit/09c1999e97558b7270124b83e90c2f5edc7a0148))

* license update ([`d9886e6`](https://github.com/nivintw/ddns/commit/d9886e69649da763b67436c3699e969a9cb1baa1))

* update license to MIT.

The original source code has either been removed or majorly re-written. ([`d911459`](https://github.com/nivintw/ddns/commit/d911459fc4420d4f2737425f04d2e6b623d41f4e))

* refactor (domains.py): remove deprecated domain_id argument. ([`48b441c`](https://github.com/nivintw/ddns/commit/48b441c855d94860c2b8b6a50389e0bef5cb72b8))

* refactor (subdomains): major refactor.

- Add TopDomainNotManagedError
  - Users should never see this exception.
- refactor list_sub_domains
- refactor list_do_unmanaged_sub_domains
- refactor manage_subdomain
- update many function names
- temporarily remove some adjacent functionality. ([`e5da24e`](https://github.com/nivintw/ddns/commit/e5da24e7c9caf2cafee1575df834cd629e54367a))

* fix (domains.py): manage_all_existing_A_records

- fix for new return value of get_A_records()
- tests (refactor tests) ([`6fa26e9`](https://github.com/nivintw/ddns/commit/6fa26e9cd90d2cce09a364dc52e6bb80585c29bf))

* tests (subdomains): update tests and add TODO ([`32c4411`](https://github.com/nivintw/ddns/commit/32c44116607ebc8bbc3112394d687bd2dcaea38e))

* refactor (database): rename id -&gt; domain_record_id for subdomains table. ([`9ac816e`](https://github.com/nivintw/ddns/commit/9ac816e5f77dae8c9efb23f2e7fc60b05de4552f))

* add TODO for tests ([`c558587`](https://github.com/nivintw/ddns/commit/c558587d62cdced66c900d3aa37cbf6493eb2802))

* add todo ([`6f85c13`](https://github.com/nivintw/ddns/commit/6f85c13d807022b156ed36098e1fbb42e01c826c))

* fix (get_all_domains()): Fix pagination.

DO API behaves differently than documented; see changes and prior commits related to pagination. ([`24e2b11`](https://github.com/nivintw/ddns/commit/24e2b11a085c3cc9322bbff382fc7d4eaa260093))

* WIP: update readme.md with notes ([`83e6aae`](https://github.com/nivintw/ddns/commit/83e6aaecd08a14846443eae633d847b10b6f6635))

* nit: fix comment in pyproject.toml ([`9fdefd8`](https://github.com/nivintw/ddns/commit/9fdefd81cda023efc23419b1c0e2da0f2bf5fa34))

* feature (get_A_records): support pagination.

One of the lessons I learned during this feature was that Digital Ocean&#39;s API docs currently don&#39;t reflect their actual behavior.
- pagination links provided by links.next etc don&#39;t retain filters e.g. type=a filter for domain records lookups.
- meta.total in the DO API response returns the total number of records that match the filter, NOT the num of records in the response i.e. meta.total does NOT account for pagination.

I reported the above two things to DO via a support ticket. ([`cbc5c03`](https://github.com/nivintw/ddns/commit/cbc5c037ecd7f8fac224c0415a46a1a5f4831a78))

* refactor (domains.py) ([`7e07b8e`](https://github.com/nivintw/ddns/commit/7e07b8e86079ea658adb7f9fb66b8115dd287022))

* Add do_api.py

Module of functionality for the Digital Ocean API. ([`29e4524`](https://github.com/nivintw/ddns/commit/29e4524d9038478ce80e7e14b93ecb6659b22304))

* add more-itertools ([`f988466`](https://github.com/nivintw/ddns/commit/f9884664477c54b69cfdbd79518e5f591f925942))

* license header update ([`c014da9`](https://github.com/nivintw/ddns/commit/c014da99cdc08acd4c2b35737089592f3833899a))

* license header changes ([`c789f08`](https://github.com/nivintw/ddns/commit/c789f08fba7b84d51bca80d79d5ed158e8f579fd))

* update licenserc.toml ([`ff5a540`](https://github.com/nivintw/ddns/commit/ff5a540ada15747a37b39fb111c0dbdc6f689b84))

* WIP ([`7a39345`](https://github.com/nivintw/ddns/commit/7a3934568613bcfb39cc022b8729531adcb7ae60))

* refactor manage_domains

update for new table schema.
update tests to check cataloged and last_managed values.
add stub for un_manage_domain.
re-org tests structure. ([`f12d028`](https://github.com/nivintw/ddns/commit/f12d028a99e76d0c1c467e6b835f2b4173721a1f))

* WIP refactor database.

Incorporate changes from updatedb.
Add new cols for managed/cataloged.
rename api column to key column.
add last_updated column for apikey table. ([`474bf75`](https://github.com/nivintw/ddns/commit/474bf758db0598661f175b0e2c43bf93b51565f9))

* update README.md

Add appendix and describe the various actions available. ([`c0e3f3a`](https://github.com/nivintw/ddns/commit/c0e3f3a30df3a65e5f40657ece760a18dddfed35))

* rename test_tlds.py -&gt; test_domains.py

Update license header template ([`f3603f6`](https://github.com/nivintw/ddns/commit/f3603f6327c056ccd13168ec07fd0446fd13cdb9))

* update readme.md ([`7057137`](https://github.com/nivintw/ddns/commit/70571376fb16948af47158f14515e1e6eac1b1a8))

* Replace requests-mock with responses.

I like responses more; couldn&#39;t remember it&#39;s name originally.
Separate tld related functions into new module.
add tests for show_all_top_domains ([`ea66897`](https://github.com/nivintw/ddns/commit/ea6689717418d8d67dca780436c976a72d5de6ca))

* enable PTH rules for ruff ([`8a192dd`](https://github.com/nivintw/ddns/commit/8a192dd0700fe0db9c99c929d0de4a83759dc95f))

* minor ruff updates ([`c516b22`](https://github.com/nivintw/ddns/commit/c516b22a49aacac01e28a419da0c5f5fe764ea61))

* hawkeye related changes ([`3051f14`](https://github.com/nivintw/ddns/commit/3051f14664a401bdd0cc5f99f321e2ce493edae7))

* update pre-commit; remove poetry references ([`9581472`](https://github.com/nivintw/ddns/commit/9581472ae907f952c4b0dec901904974fb2a0849))

* update min python version ([`935d065`](https://github.com/nivintw/ddns/commit/935d065e216aa6b10c228ae9ce805888427021e4))

* add project.urls ([`9a046b2`](https://github.com/nivintw/ddns/commit/9a046b26fdb403a8bed3f1584651701ced3817ec))

* add metadata to pyproject.toml ([`6a6a5c4`](https://github.com/nivintw/ddns/commit/6a6a5c4cee49e4333bb696cf65753547d5904750))

* switch to uv; remove poetry.

Unsure if i&#39;ll stick with this, but wanted to try it. ([`3d805d7`](https://github.com/nivintw/ddns/commit/3d805d7247af790697af7c017e7de93f0ae80725))

* version bump ([`119b2d3`](https://github.com/nivintw/ddns/commit/119b2d3670d776103b85c07c88d2172b690e1f2c))

* feature: add ability to show un-maked API key.

technically, the added feature is that the API key is now masked by default when using show_info ([`8009d48`](https://github.com/nivintw/ddns/commit/8009d4877f17f22606cf9ae804650972ad1ef3d6))

* add show_info subparser ([`a515a86`](https://github.com/nivintw/ddns/commit/a515a8639853653d951bc571cacc18f2415fc330))

* feature (UX): updates to argparse for improved UX. ([`137f938`](https://github.com/nivintw/ddns/commit/137f93854aaafcb6a2c77684b760a5b3a4d09be2))

* refactor (api()): rename api() to set_api_key() ([`76eb577`](https://github.com/nivintw/ddns/commit/76eb577a250f9243144ba47d7d14da712acd6bf1))

* refactor (subdomains.py, ddns.py, ip.py): favor exception raising and gate-checks.

Major refactor.
- remove several levels of nested logic (i.e. nested `else` clauses).
- refactor code related to `get_api()`; that function will always return the registered api key, else will raise.
- refactor code related to `get_ip()`; that function will always return the current ip address of the host, else will raise.
- add NoIPResolverServerError exception class.
- raise NoIPResolverServerError when no upstream IP resolver servers have been configured. ([`67a2e95`](https://github.com/nivintw/ddns/commit/67a2e95e978ef036658d4fd1c84cb03dc7cc4e34))

* Fix (show_current_info): Handle the case of someone calling --version without any configured ip resolvers. ([`f0f955f`](https://github.com/nivintw/ddns/commit/f0f955ff2d9eba73b9c3f8f481f9a89fe4af15b5))

* refactor (get_ip): refactor.
- use requests instead of urllib.request.
    requests is already used elsewhere; keep it consistent.
- re-raise any exceptions that occur
    prior impl. swallowed them and returned the error string, which wasn&#39;t being checked... ([`bc6f81a`](https://github.com/nivintw/ddns/commit/bc6f81a132984e9aafbf6216f2f2df8773167a98))

* update --ip-look-url default to be the actual url ([`b69f2b3`](https://github.com/nivintw/ddns/commit/b69f2b38a572bcccdc1324a74f84c8bca14e7a26))

* refactor (ip_server): move function def to ip.py

Also add docstring for this function explaining current limitations. ([`3b2b933`](https://github.com/nivintw/ddns/commit/3b2b933ca0a8c7bc1a7e3923e04774603641ee67))

* update message to point to new repo.

This project is a fork. ([`d9f5725`](https://github.com/nivintw/ddns/commit/d9f5725e762e7ba835844c96531c1f27e236d825))

* refactor (ddns.py): get_api() raises exception if no api key.

Update code-paths to accommodate new behavior. ([`ef207e5`](https://github.com/nivintw/ddns/commit/ef207e5ef907f34a8f89804077664de292c2ac97))

* fix (add_domain): Handle digital ocean error responses properly.

Prior implementation treated almost any &#34;not ok&#34; response as the domain not being registered in the account.
In particular, this would be a frustrating red-herring if the real issue was that the user had provided a bad api key, and was actually getting an unauthorized response. ([`a231ca2`](https://github.com/nivintw/ddns/commit/a231ca208e2a7988524a1f9962437e12f9986571))

* refactor (add_domain): add early return. ([`0750b04`](https://github.com/nivintw/ddns/commit/0750b0489b9d955a5d7cec05d79d323f346d5207))

* refactor (add_domain): code cleanup.

add early return and remove else guard.
remove redundant if apiKey is None: check.
 - apikey can never be none here; an exception is raised if there is no api key configured when get_api is called. ([`61e74b5`](https://github.com/nivintw/ddns/commit/61e74b56eb1262870653854445347641a6bca035))

* add initial tests for test_ddns.py ([`8599aa5`](https://github.com/nivintw/ddns/commit/8599aa5ad48b7a6ae1733b7dbd81defd21238fdd))

* tests: refactor and add mock_db_for_test fixture.

Reduce duplicated code. ([`ac62355`](https://github.com/nivintw/ddns/commit/ac6235530b3d354560455c7165b721777cf987fb))

* Fix erroneous handling of no api key situation.

Add tests for api_key_helpers.py.
Always raise an exception if get_api() is called without an api key being in the database. ([`670880c`](https://github.com/nivintw/ddns/commit/670880c9b2369624c0f64c80efbdee02fbaa57ef))

* add pytest-check and pytest-mock deps ([`1114dae`](https://github.com/nivintw/ddns/commit/1114dae75cec14f07362784c559a7416102a0902))

* update vscode tests settings ([`8373c2b`](https://github.com/nivintw/ddns/commit/8373c2bf50077c9f96d447db80a07720fbc95750))

* add pytest and tests scaffolding ([`ab10f1b`](https://github.com/nivintw/ddns/commit/ab10f1b8e7b421e36deefe3ab7a0bd3171b45e70))

* linter updates ([`5533051`](https://github.com/nivintw/ddns/commit/55330517863715019d5d08d3778fbb440fdc6b93))

* additional pre-commit hooks ([`02307be`](https://github.com/nivintw/ddns/commit/02307befdf44a43ab789c4a831922cabbe0ca5a8))

* update pre-commit configuration ([`4210fd2`](https://github.com/nivintw/ddns/commit/4210fd28c2c6bae0493e0647fce40d4d5731dffa))

* line-length related changes ([`ece6ba4`](https://github.com/nivintw/ddns/commit/ece6ba479dbcddfd33f337fc7bd0094d55bee821))

* ruff linter changes ([`99c4e6e`](https://github.com/nivintw/ddns/commit/99c4e6eae37c63b3554e00b9a1c9e78d1b4f8a44))

* update line-length to be 100.

Address ruff lint issues.
Mostly f-string related things. ([`4233ecc`](https://github.com/nivintw/ddns/commit/4233eccc7ac332fd1a964a5ba42105f8ccb13fe1))

* WIP: update argparse config to make usage more clear.

Also will address the weird e.g. args[&#34;top&#34;][0][0] things happening in the code
Address linting issues with long lines. ([`22e4e0e`](https://github.com/nivintw/ddns/commit/22e4e0eea490b08c2b762e954929c9a900483e63))

* add debug config ([`88e681d`](https://github.com/nivintw/ddns/commit/88e681d64b02a36329d05851bb42b0577a9b34d8))

* Add flake8-bandit rules to ruff ([`0dd94ce`](https://github.com/nivintw/ddns/commit/0dd94ce6c228b5d1835b14fcb76ce57622ba15bb))

* Use default ruff line-length ([`e4f494d`](https://github.com/nivintw/ddns/commit/e4f494d3fd4e1ce4b91e7dcb6992ca32a961334c))

* regenerate .gitignore ([`fcbf076`](https://github.com/nivintw/ddns/commit/fcbf076aeed998a9de704ae1ea82fd0819e3c07e))

* Flesh out the README.md file ([`acb9c7b`](https://github.com/nivintw/ddns/commit/acb9c7bb77c82a396515a6b702311cb4847d6953))

* update vscode settings to use ruff as the formatter.

Update ruff settings in pyproject.toml.
Update package description and author.
Update minimum version of ruff for dev dependencies. ([`0b87d17`](https://github.com/nivintw/ddns/commit/0b87d17d799729e8f263eefcbdb9de08abc9dffd))

* Update readme.md

Original repo no longer reachable for me. ([`022a0c8`](https://github.com/nivintw/ddns/commit/022a0c86b7a6c607458b55fed5fd10b28fd06831))

* ruff ([`0a40afc`](https://github.com/nivintw/ddns/commit/0a40afcae03dd7c3cc0da194b16b7fa1bc84a0f9))

* update things ([`91e515b`](https://github.com/nivintw/ddns/commit/91e515b97a7c5bb9743320bcd3f856776868438d))

* update lockfile ([`26cd560`](https://github.com/nivintw/ddns/commit/26cd5602c10c92442b58cf64eff7b2e7a1d350d2))

* s ([`b6131d6`](https://github.com/nivintw/ddns/commit/b6131d67b98fa511e3df23d40a1607fe86c4c0ac))

* start switching to sub-parsers ([`b2112af`](https://github.com/nivintw/ddns/commit/b2112af3cd97f20f717cc6b604e398173c388fe9))

* bugfix for script entrypoint ([`6389d89`](https://github.com/nivintw/ddns/commit/6389d8941283355f4febdfb8fcef1fbbf0fd5d3c))

* looser python constraint ([`aae314f`](https://github.com/nivintw/ddns/commit/aae314f50f394d6669454a906bac0cbd00fef656))

* Update README.md ([`8cb93ed`](https://github.com/nivintw/ddns/commit/8cb93edd5d0e1878761fe0d741e5eba809aaa7b5))

* initial commit and re-org ([`c99f204`](https://github.com/nivintw/ddns/commit/c99f2048f2c5fc556ba2f0339bf7305131282298))

* Update README.md ([`533d62b`](https://github.com/nivintw/ddns/commit/533d62b1847a1b7ed3e3914fff9670ef11dc70a6))

* Update README.md ([`4d89973`](https://github.com/nivintw/ddns/commit/4d899731295a754b77cb5c250b3b5d58f017e759))

* Initial commit ([`b836666`](https://github.com/nivintw/ddns/commit/b836666b123e0ccc966d68c4b5484c0eaf8dd3a7))
