# TEST 101 - Devices load

## Test purpose

To evaluate how the different microservices perform under heavy load.

## Test environment

* The backend databases are populated with all devices accepted.
* All devices are actively requesting the backend for deployments and sending
  their inventory.

## Test procedure

* Keep the system passively working under the desired load for 30 minutes

## Test metrics

* CPU and Memory mean usage for main Mender microservices
  - Expectation: to increase as the server load increases, but always keeping a
    healthy distance from their defined limits
* Devices API average response time
  - Expectation: to increase as the server load increases, but to remain in the
    order of few microseconds
