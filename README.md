# Mender Load Test

Mender is an open source over-the-air (OTA) software updater for embedded Linux
devices. Mender comprises a client running at the embedded device, as well as a
server that manages deployments across many devices.

![Mender
logo](https://raw.githubusercontent.com/mendersoftware/mender/master/mender_logo.png)

This repository contains the tool and documentation that we use when performing
the Mender Load Testing.

## Testing tool

The testing tool is written in Python. It consists on an API module to manage
the communication with the Mender Server and a set of interactive and
non-interactive scripts to control the test environment during the testing.

All the details can be found in `tool/` directory.

## Test documentation

The actual tests are performed in a semi-automated manner. There is a test
specification and a set of tools to perform the tests, and it is the
responsibility of the tester engineer to prepare the test environments, monitor
the progress and collect the test metrics.

The test procedures and setup notes can be found in `doc/` directory.

## Contributing

We welcome and ask for your contribution. If you would like to contribute to
Mender, please read our guide on how to best get started [contributing code or
documentation](https://github.com/mendersoftware/mender/blob/master/CONTRIBUTING.md).

## License

Mender is licensed under the Apache License, Version 2.0. See
[LICENSE](https://github.com/mendersoftware/mender-client-python-example/blob/master/LICENSE)
for the full license text.

## Security disclosure

We take security very seriously. If you come across any issue regarding
security, please disclose the information by sending an email to
[security@mender.io](security@mender.io). Please do not create a new public
issue. We thank you in advance for your cooperation.

## Connect with us

* Join the [Mender Hub discussion forum](https://hub.mender.io)
* Follow us on [Twitter](https://twitter.com/mender_io). Please feel free to
  tweet us questions.
* Fork us on [Github](https://github.com/mendersoftware)
* Create an issue in the [bugtracker](https://northerntech.atlassian.net/projects/MEN)
* Email us at [contact@mender.io](mailto:contact@mender.io)
* Connect to the [#mender IRC channel on Libera](https://web.libera.chat/?#mender)
