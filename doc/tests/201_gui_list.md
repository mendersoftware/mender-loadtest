# TEST 201 - GUI Listing devices

## Test purpose

To evaluate how responsible the Devices panel in the Mender GUI is when the
backend is working under heavy loads.

## Test environment

* The backend databases are populated with all devices accepted.
* All devices are actively requesting the backend for deployments and sending
  their inventory.

## Test procedure

* Log in into the UI (preferably using a private window in the browser)
* Go to devices tab, accepted devices, All devices
* Set pagination to 50
* During 5 minutes, browse the devices list for ~5 minutes, for example
  * click next page few times
  * click prev page few times
  * go to last page
  * select any page to go to
  * expand a device
  * change pagination
  * ...
* Log out from ui, close tab

## Test metrics

* Devices API response time
  - Expectation: to remain the same as without using the GUI
* Management API response time
  - Expectation: to increase as the server load increases, but to remain in
    "human acceptable" values
