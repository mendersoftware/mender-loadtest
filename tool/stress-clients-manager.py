#!/usr/bin/env python3

import configargparse
import logging

from random import randint
from time import strftime

from boto3 import session


logs_format = "[%(asctime)s] [%(levelname)-8s] %(message)s"
logging.basicConfig(format=logs_format, level=logging.INFO)
log = logging.getLogger()


class StressClientManager:
    instance_type = None
    aws_ec2_region = None
    aws_s3_region = None
    ssh_key_name = None
    image_id = None
    s3_bucket_name = None
    s3_bucket_files_prefix = None

    instance_ids = []
    s3_bucket_files_list = None
    random_instance_tag_prefix = randint(10, 99)
    is_cleaned = False
    ec_2session = None
    ec2_client = None
    ec2_resource = None
    s3_session = None
    s3_client = None

    def __init__(
        self,
        ssh_key_name=None,
        instance_type="t2.micro",
        ec2_region="us-east-1",
        s3_region="us-east-1",
        image_id="ami-0ac05733838eabc06",
        s3_bucket_name="stresstesting-keys",
        s3_bucket_files_prefix="keys",
    ):
        self.instance_type = instance_type
        self.ec2_region_name = ec2_region
        self.s3_region_name = s3_region
        self.ssh_key_name = ssh_key_name
        self.image_id = image_id
        self.s3_bucket_name = s3_bucket_name
        self.s3_bucket_files_prefix = s3_bucket_files_prefix

    def create_instance(self, user_data):
        """
        Makes API calls to AWS EC2 to create an instance and sets a label on it
        :param user_data: 'string' user data script to configure an instance and run container with stress client
        :return: 'string' instance id
        """
        self._ec2_establish_communication()
        instance = self.ec2_resource.create_instances(
            ImageId=self.image_id,
            MinCount=1,
            MaxCount=1,
            KeyName=self.ssh_key_name,
            UserData=user_data,
            InstanceType=self.instance_type,
        )[0]
        self.instance_ids.append(instance.instance_id)
        self.ec2_client.create_tags(
            Resources=[instance.instance_id],
            Tags=[
                {
                    "Key": "Name",
                    "Value": "stress-test-client-%s-%s"
                    % (self.random_instance_tag_prefix, len(self.instance_ids)),
                }
            ],
        )
        return instance.instance_id

    def get_keys_archives_list(self, is_force=False):
        """
        Makes a call to AWS S3 to get a list of all files (archives with pre-generated RSA keys for stress test client)
        from specified folder (specified prefix = folder name)
        :param is_force: 'boolean' overwrite current list by fresh one
        :return: 'list' files list in bucket
        """
        self._s3_establish_communication()
        if not self.s3_bucket_files_list or is_force:
            self.s3_bucket_files_list = self.s3_client.list_objects_v2(
                Bucket=self.s3_bucket_name, Prefix=self.s3_bucket_files_prefix
            )
        return self.s3_bucket_files_list

    def get_archive_name(self, index):
        """
        Returns file name (archive with pre-generated RSA keys for stress test client) by id in list
        :param index: 'int' number in s3_bucket_files_list list
        :return: 'sting' file (archive) name including prefix (folder)
        """
        return self.s3_bucket_files_list["Contents"][index]["Key"]

    def get_download_url(self, file_name):
        """
        Makes API call to AWS S3 to generate a URL for file download
        :param file_name: 'string' name of a file to which generate download link
        :return: 'string' download URL
        """
        self._s3_establish_communication()
        return self.s3_client.generate_presigned_url(
            "get_object", Params={"Bucket": self.s3_bucket_name, "Key": file_name}
        )

    def do_cleanup(self, instance_ids=None):
        """
        Makes API call to AWS EC2 to terminate all created instances
        :param instance_ids: 'list' of instance ids
        :return: 'boolean' call execution state
        """
        self._ec2_establish_communication()
        if instance_ids:
            instances_to_delete = instance_ids
        else:
            instances_to_delete = self.instance_ids
        if len(instances_to_delete) > 0:
            self.ec2_resource.instances.filter(
                InstanceIds=instances_to_delete
            ).terminate()
            self.is_cleaned = True
        return self.is_cleaned

    def _ec2_establish_communication(self):
        if (
            self.ec_2session is None
            or self.ec2_client is None
            or self.ec2_resource is None
        ):
            self.ec_2session = session.Session(region_name=self.ec2_region_name)
            self.ec2_client = self.ec_2session.client("ec2")
            self.ec2_resource = self.ec_2session.resource("ec2")

    def _s3_establish_communication(self):
        if not self.s3_session or not self.s3_client:
            self.s3_session = session.Session(region_name=self.s3_region_name)
            self.s3_client = self.s3_session.client("s3")


stress_test_client_image = ""
stress_test_client_startup_interval = 0
stress_test_client_inventory_freq = 0
stress_test_client_poll_interval_freq = 0
aws_instance_type = ""
aws_instance_image_id = ""
aws_ec2_region = ""
aws_s3_region = ""
aws_s3_bucket_name = ""
aws_s3_bucket_files_prefix = ""
server_url = ""
aws_ssh_key_name = ""
tenant_key = ""
start_count = 0
devices_qty = 1

user_data_template = """#!/bin/bash
set -e
apt-get update
apt-get install -y apt-transport-https ca-certificates curl wget gnupg-agent software-properties-common
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | apt-key add -
add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
apt-get update
apt-get install -y docker-ce docker-ce-cli containerd.io
FILE_NAME=$(echo {file} | sed 's/{prefix}\\///g')
wget -O $FILE_NAME "{download_url}"
tar -zxf $FILE_NAME
mv $(echo $FILE_NAME | sed 's/\\.tgz//g') /keys
docker run -d -v /keys:/keys {image} -count {count} -startup-interval {start_interval} -backend {server_url} \
    -invfreq {inventory_interval} -pollfreq {poll_interval} -wait 30 -current_artifact base-image-1019 \
    -current_device cl-som-imx8 -inventory device_type:cl-som-imx8,image_id:base-image-1019 -tenant {tenant_key}
"""
# TODO: make the following options configurable: wait, current_artifact, current_device and inventory


def terminate_instances(instances_list_to_delete_file, aws_ec2_region):
    instance_ids_to_delete = []
    with open(instances_list_to_delete_file, "r") as file:
        for line in file:
            instance_ids_to_delete.append(line.rstrip())
    _stress_client_manager = StressClientManager(ec2_region=aws_ec2_region)
    _stress_client_manager.do_cleanup(instance_ids_to_delete)
    log.info("Instances from '%s' terminated." % conf.instances_list_to_delete_file)
    exit(0)


def start_instances_in_non_interactive_session():
    stress_client_manager = StressClientManager(
        ssh_key_name=aws_ssh_key_name,
        instance_type=aws_instance_type,
        ec2_region=aws_ec2_region,
        s3_region=aws_s3_region,
        image_id=aws_instance_image_id,
        s3_bucket_name=aws_s3_bucket_name,
        s3_bucket_files_prefix=aws_s3_bucket_files_prefix,
    )
    stress_client_manager.get_keys_archives_list()

    global devices_qty
    count = start_count
    # get archive name with rsa keys and generate download link for it
    archive_name = stress_client_manager.get_archive_name(count)
    download_url = stress_client_manager.get_download_url(archive_name)
    # make user data script from template
    user_data_prepared = user_data_template.format(
        file=archive_name,
        prefix=stress_client_manager.s3_bucket_files_prefix,
        download_url=download_url,
        image=stress_test_client_image,
        count=devices_qty,
        start_interval=stress_test_client_startup_interval,
        server_url=server_url,
        inventory_interval=stress_test_client_inventory_freq,
        poll_interval=stress_test_client_poll_interval_freq,
        tenant_key=tenant_key,
    )

    # start instance
    instance_id = stress_client_manager.create_instance(user_data=user_data_prepared)
    log.info(
        "Started instance %s, devices qty: %s, start count: %s"
        % (instance_id, devices_qty, start_count)
    )


def start_interactive_session():
    stress_client_manager = StressClientManager(
        ssh_key_name=aws_ssh_key_name,
        instance_type=aws_instance_type,
        ec2_region=aws_ec2_region,
        s3_region=aws_s3_region,
        image_id=aws_instance_image_id,
        s3_bucket_name=aws_s3_bucket_name,
        s3_bucket_files_prefix=aws_s3_bucket_files_prefix,
    )
    stress_client_manager.get_keys_archives_list()

    # read from stdin and start instances
    try:
        count = start_count
        while True:
            command = input("'<int>'|'cleanup': ")
            if command == "cleanup":
                log.info("cleaning up ...")
                stress_client_manager.do_cleanup()
                exit(0)
            try:
                devices_qty = int(command)
                if devices_qty > 10000 or devices_qty < 1:
                    log.warning("Allowed range is 1..10k")
                    continue
            except ValueError as e:
                if command != "":
                    log.warning(e)
                continue

            log.info("Starting instance with '%s' stress clients." % devices_qty)

            # get archive name with rsa keys and generate download link for it
            archive_name = stress_client_manager.get_archive_name(count)
            download_url = stress_client_manager.get_download_url(archive_name)

            # make user data script from template
            user_data_prepared = user_data_template.format(
                file=archive_name,
                prefix=stress_client_manager.s3_bucket_files_prefix,
                download_url=download_url,
                image=stress_test_client_image,
                count=devices_qty,
                start_interval=stress_test_client_startup_interval,
                server_url=server_url,
                inventory_interval=stress_test_client_inventory_freq,
                poll_interval=stress_test_client_poll_interval_freq,
                tenant_key=tenant_key,
            )

            # start instance
            instance_id = stress_client_manager.create_instance(
                user_data=user_data_prepared
            )
            log.info("Instance %s started" % instance_id)

            count += 1

    except KeyboardInterrupt:
        # save created instances list to a file if cleanup wasn't done
        if (
            not stress_client_manager.is_cleaned
            and len(stress_client_manager.instance_ids) > 0
        ):
            instances_list_file_name = (
                "instances-list_" + strftime("%Y%m%d-%H%M%S") + ".txt"
            )
            with open(instances_list_file_name, "w") as f:
                for instance_id in stress_client_manager.instance_ids:
                    f.write("%s\n" % instance_id)
            log.info(
                "List of created instances saved into '%s'" % instances_list_file_name
            )
        # new line for better view in console
        print("")
        exit(0)


def get_config():
    default_image = "mendersoftware/mender-stress-test-client:intervalstart_414931815b2af000f4be2e8fde1f0c5098aafe29"

    parser = configargparse.ArgumentParser()
    parser.add_argument(
        "--instances-list-to-delete-file",
        type=str,
        required=False,
        default=None,
        help="File with instances list for termination separated by new line.",
    )
    parser.add_argument(
        "--stress-test-client-image",
        type=str,
        required=False,
        default=default_image,
        help="mender-stress-test-client image.",
        env_var="STRESS_TEST_CLIENT_IMAGE",
    )
    parser.add_argument(
        "--stress-test-client-startup-interval",
        type=str,
        required=False,
        default="1750000",
        help="Stress test client startup interval",
        env_var="STRESS_TEST_CLIENT_STARTUP_INTERVAL",
    )
    parser.add_argument(
        "--stress-test-client-inventory-freq",
        type=str,
        required=False,
        default="28800",
        help="Inventory update interval.",
        env_var="STRESS_TEST_CLIENT_INVENTORY_FREQ",
    )
    parser.add_argument(
        "--stress-test-client-poll-interval-freq",
        type=str,
        required=False,
        default="1800",
        help="Poll interval.",
        env_var="STRESS_TEST_CLIENT_POLL_INTERVAL_FREQ",
    )
    parser.add_argument(
        "--aws-instance-type",
        type=str,
        required=False,
        default="c5.large",
        help="AWS instance type.",
        env_var="AWS_INSTANCE_TYPE",
    )
    parser.add_argument(
        "--aws_instance_image_id",
        type=str,
        required=False,
        default="ami-0ac05733838eabc06",
        help="AWS instance image id.",
        env_var="AWS_INSTANCE_IMAGE_ID",
    )
    parser.add_argument(
        "--aws-ec2-region",
        type=str,
        required=False,
        default="us-east-1",
        help="AWS EC2 region.",
        env_var="AWS_EC2_REGION",
    )
    parser.add_argument(
        "--aws-s3-region",
        type=str,
        required=False,
        default="us-east-1",
        help="AWS S3 region.",
        env_var="AWS_S3_REGION",
    )
    parser.add_argument(
        "--aws-s3-bucket-name",
        type=str,
        required=False,
        default="stresstesting-keys",
        help="AWS S3 bucket name where keys are stored.",
        env_var="AWS_S3_BUCKET_NAME",
    )
    parser.add_argument(
        "--aws-s3-bucket-files-prefix",
        type=str,
        required=False,
        default="keys",
        help="AWS S3 bucket prefix (folder with keys).",
        env_var="AWS_S3_BUCKET_PREFIX",
    )
    parser.add_argument(
        "--server-url",
        type=str,
        required=False,
        default=None,
        help="Mender backend URL.",
        env_var="MENDER_SEVER_URL",
    )
    parser.add_argument(
        "--aws-ssh-key-name",
        type=str,
        required=False,
        default=None,
        help="Public key name (how its saved in AWS).",
        env_var="AWS_SSH_KEY_NAME",
    )
    parser.add_argument(
        "--tenant-key",
        type=str,
        required=False,
        default=None,
        help="Mender tenant key.",
        env_var="TENANT_KEY",
    )
    parser.add_argument(
        "--start-count",
        type=int,
        required=False,
        default=None,
        help="Sequence number of instance to start.",
        env_var="START_COUNT",
    )
    parser.add_argument(
        "--devices-qty",
        type=int,
        required=False,
        default=1,
        help="Number of devices to start.",
        env_var="DEVICES_QTY",
    )
    parser.add_argument(
        "--non-interactive-mode",
        type=bool,
        required=False,
        default=False,
        help="Execute in non interactive mode.",
        env_var="NON_INTERACTIVE_MODE",
    )
    return parser.parse_args()


def process_config(config):
    global stress_test_client_image
    global stress_test_client_startup_interval
    global stress_test_client_inventory_freq
    global stress_test_client_poll_interval_freq
    global aws_instance_type
    global aws_instance_image_id
    global aws_ec2_region
    global aws_s3_region
    global aws_s3_bucket_name
    global aws_s3_bucket_files_prefix
    global server_url
    global aws_ssh_key_name
    global tenant_key
    global start_count
    global devices_qty

    stress_test_client_image = config.stress_test_client_image
    stress_test_client_startup_interval = config.stress_test_client_startup_interval
    stress_test_client_inventory_freq = config.stress_test_client_inventory_freq
    stress_test_client_poll_interval_freq = config.stress_test_client_poll_interval_freq
    aws_instance_type = config.aws_instance_type
    aws_instance_image_id = config.aws_instance_image_id
    aws_ec2_region = config.aws_ec2_region
    aws_s3_region = config.aws_s3_region
    aws_s3_bucket_name = config.aws_s3_bucket_name
    aws_s3_bucket_files_prefix = config.aws_s3_bucket_files_prefix
    server_url = config.server_url
    aws_ssh_key_name = config.aws_ssh_key_name
    tenant_key = config.tenant_key
    start_count = config.start_count
    devices_qty = config.devices_qty

    if start_count is None:
        start_count = 0


if __name__ == "__main__":
    conf = get_config()

    # if instances list file specified, then do instances termination and exit
    if conf.instances_list_to_delete_file is not None:
        terminate_instances(conf.instances_list_to_delete_file, conf.aws_ec2_region)

    # mandatory options to proceed
    if (
        conf.server_url is None
        or conf.aws_ssh_key_name is None
        or conf.tenant_key is None
    ):
        log.error(
            "pass MENDER_SEVER_URL, TENANT_KEY and AWS_SSH_KEY_NAME env vars or params."
        )
        exit(1)

    process_config(conf)

    if conf.non_interactive_mode:
        start_instances_in_non_interactive_session()
    else:
        start_interactive_session()
