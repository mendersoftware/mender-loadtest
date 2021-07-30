# TEST 301 - Deployment

## Test purpose

To evaluate whether the system can deploy to a 10% of its active fleet on one
deployment polling interval (30 minutes).

## Test environment

* The backend databases are populated with all devices accepted.
* All devices are actively requesting the backend for deployments and sending
  their inventory.

## Test procedure

* Start a deployment for the 10% of the fleet (the size of the Artifact is
  irrelevant)
* All targeted devices shall get the update in one single deployment polling
  interval (30 minutes)

## Test metrics

* CPU and Memory max usage for mender-api-gateway, mender-deployments and
  mender-inventory.
  - Expectation: to heavily increase while the deployment is in progress, but
    keeping the values below their defined limits.
* Devices API peak response time
  - Expectation: to increase as the server load increases, but to remain in the
    order of hundreds of microseconds
