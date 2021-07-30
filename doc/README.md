# Load testing documentation

This repository collects setup notes, test procedures, test logs and test
reports for Mender Load Testing.

The defined tests can be found at `tests/` subfolder, while the log and report
for the performed tests can be found at `test-<date>` directories.

## Test definitions

The tests are being added to `tests/` as we develop them. Try to add tests
following the pattern:
* `1xx_short_id` for passive tests
* `2xx_short_id` for manual GUI tests
* `3xx_short_id` for active tests

If a test requires an update such that will fundamentally change the procedure
or the metrics to collect, just create a new one and mark the previous one as
"deprecated", so that old reports still refer to exiting definitions.

## Test reports and test log

Every time we perform tests, we shall create a new `test-<date>` directory. The
format and style of the test report and log is up to the tester, the most
important parts are:
* To have a human readable test report with at least:
  - Executive summary of the main results
  - Important issues discovered during testing
* Test results, preferably on a spreadsheet to easily create graphs
* To have some sort of test log that serves as a basic traceability of the job
  done

## Fist time setup

This chapter assumes you have deployed production grade Mender on an given
Kubernetes cluster and that the backend is accessible via internet.

First sign up via UI, as you would do on a regular production environment

Then SSH into mongodb primary node to:

1. Remove trial:
```
use tenantadm
db.tenants.find()
db.tenants.updateOne( { "_id" : "6066fec255ac6b41d17401be"}, [  { $set: { "trial" : false} },  { $unset: ["trial_expiration"]}])
```

2. Remove limit:
```
use deviceauth-6066fec255ac6b41d17401be
db.limits.updateOne( { "_id" : "max_devices"}, [  { $set: { "value" : NumberLong(0)} }])
```

After these tweaks, the server is ready to start getting devices load.

## Mender stress test client

To generate the load, we use
[mender-stress-test-client](https://github.com/mendersoftware/mender-stress-test-client).
We configure the stress test client to use Mender default production polling
intervals:
* Inventory update every 8 hours
* Deployment poll every 30 minutes

To achieve a constant on the server, we set the start-up time of the clients to
match the inventory poll interval (8h). This means that on the very first
set-up, we need to wait this time since starting the clients until the desired
load is achieved.
