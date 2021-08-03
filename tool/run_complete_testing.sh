#!/usr/bin/env bash

log() {
    echo "[$(date +%Y-%m-%d\ %T)] $1"
}

start_fake_clients() {
    local start_count=$1
    local devices_qty=$2
    ./stress-clients-manager.py --aws-ec2-region $ec2_region --aws-s3-region $s3_region --server-url $server_url --aws-ssh-key-name $ssh_key_name --tenant-key $token --stress-test-client-startup-interval 1799000 --non-interactive-mode True --start-count $start_count --devices-qty $devices_qty
}

open_browser() {
    # make sure that chrome container is not running
    docker ps | grep -q chrome_container
    if [ $? -eq 0 ]; then
        docker stop chrome_container > /dev/null
    fi
    # start container with chrome browser
    docker run --rm --name chrome_container -p 4444:4444 -d selenium/standalone-chrome > /dev/null
    sleep 5

    # using selenium webdriver login and keep browser open for 10 mins
    ./selenium_login_to_ui_and_sleep.py

    # cleanup
    docker ps | grep -q chrome_container
    if [ $? -eq 0 ]; then
        docker stop chrome_container > /dev/null
    fi
    docker ps -a | grep chrome_container | grep -q Exited
    if [ $? -eq 0 ]; then
        docker rm chrome_container > /dev/null
    fi
}

run_ui_phase() {
    open_browser
    ./do_deployment_to_all_devices.py
    open_browser
    open_browser
    open_browser
}

accept_devices() {
    ./accept_all_devices.py
}

do_deployment() {
    ./do_deployment_to_all_devices.py
}

check_accepted_devices_qty() {
    current_accepted_devices_qty=$(./get_number_of_devices.py accepted)
    if [ "$current_accepted_devices_qty" -ne "$total_devices" ]; then
        log "WARNING: number of accepted devices is '$current_accepted_devices_qty' which is not as expected '$total_devices'"
    fi
}


[ -z "$TOKEN" ] && { echo "ERROR: TOKEN is empty"; exit 1; }
[ -z "$SSH_KEY_NAME" ] && { echo "ERROR: SSH_KEY_NAME is empty"; exit 1; }
[ -z "$URL" ] && { echo "ERROR: URL is empty"; exit 1; }
[ -z "$USERNAME" ] && { echo "ERROR: USERNAME is empty"; exit 1; }
[ -z "$PASSWORD" ] && { echo "ERROR: PASSWORD is empty"; exit 1; }
[ -z "$ARTIFACT_NAME" ] && {
    log "WARNING: ARTIFACT_NAME is empty using default 'release-1'";
    export ARTIFACT_NAME='release-1';
}


devices=(100 400 500 4000 5000)
start_count=${START_COUNT:-1}
devices_array_index=${DEVICES_INDEX:-0}
token=$TOKEN
server_url="https://$URL"
s3_region=${S3_REGION:-"us-east-1"}
ec2_region=${EC2_REGION:-"eu-central-1"}
ssh_key_name=$SSH_KEY_NAME
total_devices=0
export URL="https://$URL"

# '14' here is 100k devices: first 5 gives 10k and rest 9 gives 90k
while [ $devices_array_index -lt 14 ]; do
    # start fake clients
    if [ $devices_array_index -lt ${#devices[@]} ]; then
        devices_qty=${devices[$devices_array_index]}
    else
        devices_qty=10000
    fi
    start_fake_clients $start_count $devices_qty
    let devices_array_index=$devices_array_index+1
    let start_count=$start_count+1
    let total_devices=$total_devices+$devices_qty

    # wait 1.5 hours
    log "sleep for 1.5 hours"
    sleep 5400

    # accept all devices
    accept_devices

    # check number of accepted devices
    log "Checking number of accepted devces"
    check_accepted_devices_qty

    # wait 30 mins
    log "sleep for 30 mins"
    sleep 1800

    # create deployment to all devices from CLI
    log "expected qty of accepted devices is '$total_devices'"
    do_deployment

    # waint 45 mins
    log "sleep for 45 mins"
    sleep 2700

    # open browser for 40 mins and do deployment from UI
    run_ui_phase

    # wait 30 mins
    log "sleep for 30 mins"
    sleep 1800
done

log "Execution finished."

