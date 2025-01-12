# author: Luka Pacar
import time
from datetime import date, datetime
import pytz

import boto3
from botocore.exceptions import ClientError

from vm import VirtualMachine, Provider


class AWS(Provider):
    """AWS cloud provider implementation."""

    def __init__(self, account_name: str, connection_date: date, access_key: str, secret_key: str, region: str,
                 vpc_id: str = None, subnet_id: str = None, security_group_id: str = None):
        super().__init__(account_name, connection_date)
        self.provider_info_string = self.get_provider_name() + self.starting_character + f"{access_key}{Provider.delimiter}{secret_key}{Provider.delimiter}{region}{Provider.delimiter}{vpc_id}{Provider.delimiter}{subnet_id}{Provider.delimiter}{security_group_id}"
        self.access_key = access_key
        self.secret_key = secret_key
        self.region = region
        if vpc_id == "None":
            vpc_id = None
        if subnet_id == "None":
            subnet_id = None
        if security_group_id == "None":
            security_group_id = None
        self.vpc_id = vpc_id
        self.subnet_id = subnet_id
        self.security_group_id = security_group_id
        self.client = boto3.client(
            'ec2',
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            region_name=self.region
        )

    @staticmethod
    def from_provider_info(account_name: str, connection_date: date, provider_info: str):
        """Creates a Provider object from the provider information."""
        access_key, secret_key, region, vpc_id, subnet_id, security_group_id = \
            provider_info.split(Provider.starting_character)[1].split(Provider.delimiter)
        return AWS(account_name, connection_date, access_key, secret_key, region, vpc_id, subnet_id, security_group_id)

    def get_provider_name(self) -> str:
        """Returns the name of the provider (AWS)."""
        return "AWS"

    def get_provider_info(self) -> str:
        """Returns information about the provider."""
        return self.get_provider_name() + self.starting_character + f"{self.access_key}{Provider.delimiter}{self.secret_key}{Provider.delimiter}{self.region}{Provider.delimiter}{self.vpc_id}{Provider.delimiter}{self.subnet_id}{Provider.delimiter}{self.security_group_id}"

    def connection_is_alive(self, print_output=True) -> bool:
        """Verifies if AWS credentials and connection work."""
        try:
            self.client.describe_regions()
            print("Authenticated successfully.") if print_output else None
            return True
        except ClientError as e:
            print(f"Authentication failed: {e}") if print_output else None
            return False

    def create_resources(self, location: str, print_output=True):
        """Creates VPC, subnet, security group only if not already created."""
        try:
            if self.vpc_id is None:
                # Create a VPC
                vpc = self.client.create_vpc(CidrBlock='10.0.0.0/16')
                self.vpc_id = vpc['Vpc']['VpcId']

                # Create an Internet Gateway and attach it to the VPC
                internet_gateway = self.client.create_internet_gateway()
                internet_gateway_id = internet_gateway['InternetGateway']['InternetGatewayId']
                self.client.attach_internet_gateway(VpcId=self.vpc_id, InternetGatewayId=internet_gateway_id)

                # Create a public subnet
                subnet = self.client.create_subnet(
                    VpcId=self.vpc_id, CidrBlock='10.0.1.0/24', AvailabilityZone=location + 'a')

                # Enable auto-assign public IP feature after subnet creation
                self.client.modify_subnet_attribute(
                    SubnetId=subnet['Subnet']['SubnetId'],
                    MapPublicIpOnLaunch={'Value': True}  # Enables auto-assigning of public IPs
                )

                self.subnet_id = subnet['Subnet']['SubnetId']

                # Create a Route Table and associate it with the subnet (so it can access the Internet Gateway)
                route_table = self.client.create_route_table(VpcId=self.vpc_id)
                route_table_id = route_table['RouteTable']['RouteTableId']
                self.client.create_route(
                    RouteTableId=route_table_id,
                    DestinationCidrBlock='0.0.0.0/0',
                    GatewayId=internet_gateway_id
                )
                self.client.associate_route_table(RouteTableId=route_table_id, SubnetId=self.subnet_id)

                # Create a Security Group with no restrictions (open to all traffic)
                security_group = self.client.create_security_group(
                    GroupName='AllowAllTraffic', Description='Allow all inbound/outbound traffic', VpcId=self.vpc_id)
                self.security_group_id = security_group['GroupId']
                self.client.authorize_security_group_ingress(
                    GroupId=self.security_group_id,
                    IpProtocol='-1',  # Allow all traffic
                    CidrIp='0.0.0.0/0'
                )

                print("\033[32mCreated VPC, subnet, security group and associated resources.\033[0m") if print_output else None

        except ClientError as e:
            print(f"Failed to create resources: {e}")

    def create_vm(self, vm_name: str, aws_ssh_key_name: str, zerotier_network: str, ssh_key_path: str = "EvaluateSelf", location: str = "eu-central-1", vm_size: str = "t3.micro",
                  admin_password: str = "YourSecurePassword!", image_reference: str = "ami-079cb33ef719a7b78",
                  max_retries: int = 1000, retry_interval: int = 10, print_output=True):
        """
        Creates an EC2 instance on AWS with public access (reachable from the internet).

        :param vm_name: Name of the VM.
        :param aws_ssh_key_name: Name of the SSH key pair used. public key has to be on AWS. private key has to be under ~/.ssh/.
        :param zerotier_network: ZeroTier network ID.
        :param ssh_key_path: Path to the SSH key file. (default: ~/.ssh/[aws_ssh_key_name].pem)
        :param location: AWS region (default: eu-central-1, Frankfurt region).
        :param vm_size: Instance type (default: t3.micro, free-tier eligible).
        :param admin_password: Admin password for tagging. (default: YourSecurePassword!) - Not that important because of SSH key authentication.
        :param image_reference: Image reference (default: Ubuntu 20.04 LTS AMI ID).
        :param max_retries: Maximum retries for load (until the VM gets an IP).
        :param retry_interval: Time in seconds between each Public-IP-Test-Retry.
        :param print_output: Print outputs with useful info.
        """
        if ssh_key_path == "EvaluateSelf":
            ssh_key_path = f"~/.ssh/{aws_ssh_key_name}.pem"
        try:
            # Make sure resources are created if not already done
            if self.vpc_id is None or self.subnet_id is None or self.security_group_id is None:
                self.create_resources(location, print_output)
            else:
                print("Found existing resources. Skipping creation.") if print_output else None

            # EC2 instance configuration
            params = {
                "ImageId": image_reference,
                "InstanceType": vm_size,
                "KeyName": aws_ssh_key_name,
                "MinCount": 1,
                "MaxCount": 1,
                "SubnetId": self.subnet_id,  # Attach VM to existing subnet
                "SecurityGroupIds": [self.security_group_id],  # Attach VM to existing security group
                "TagSpecifications": [
                    {
                        "ResourceType": "instance",
                        "Tags": [
                            {"Key": "Name", "Value": vm_name},
                            {"Key": "AdminPassword", "Value": admin_password}
                        ]
                    }
                ]
            }

            print(f"\033[31mVM '{vm_name}' is being created...\033[32m") if print_output else None
            instance = self.client.run_instances(**params)['Instances'][0]

            instance_id = instance['InstanceId']
            print(f"VM '{vm_name}' created. Instance ID: {instance_id}\033[0m") if print_output else None

            # Wait for the instance to be running
            retries = 0
            public_ip = None
            while retries < max_retries:
                instance_info = \
                    self.client.describe_instances(InstanceIds=[instance_id])['Reservations'][0]['Instances'][0]
                state = instance_info['State']['Name']

                if state == 'running':
                    public_ip = instance_info.get('PublicIpAddress', "Pending")
                    print(f"\033[32mInstance '{vm_name}' is running. \033[34mPublic IP: {public_ip}\033[0m") if print_output else None
                    break
                else:
                    print(f"\033[33mInstance '{vm_name}' state: {state}\033[0m") if print_output else None

                retries += 1
                time.sleep(retry_interval)

            if not public_ip:
                print(f"Failed to get public IP for instance '{vm_name}' after {max_retries} retries.") if print_output else None
                return None

            # Return the VirtualMachine object
            return VirtualMachine(
                vm_name,
                self,
                -1,
                public_ip,
                date.today(),
                "ubuntu",
                admin_password,
                zerotier_network,
                ssh_key_path
            )

        except ClientError as e:
            print(f"Failed to create VM '{vm_name}': {e}")
            return None

    def stop_vm(self, vm: VirtualMachine, print_output=True):
        """Stops an EC2 instance on AWS."""
        instance_name = vm.get_vm_name()
        try:

            # Get the instance ID by the instance name
            instance_id = self.get_instance_id_by_name(instance_name)

            # Stop the instance using the instance ID
            self.client.stop_instances(InstanceIds=[instance_id])
            print(f"Stopping VM '{instance_name}' (ID: {instance_id}).") if print_output else None
        except ClientError as e:
            print(f"Failed to stop VM '{instance_name}': {e}")

    def start_vm(self, vm: VirtualMachine, print_output=True):
        """Stops an EC2 instance on AWS."""
        instance_name = vm.get_vm_name()
        try:

            # Get the instance ID by the instance name
            instance_id = self.get_instance_id_by_name(instance_name)

            # Stop the instance using the instance ID
            self.client.start_instances(InstanceIds=[instance_id])
            print(f"Starting VM '{instance_name}' (ID: {instance_id}).") if print_output else None

        except ClientError as e:
            print(f"Failed to start VM '{instance_name}': {e}")

    def delete_vm(self, vm: VirtualMachine, db, print_output=True):
        """Deletes an EC2 instance on AWS."""
        instance_name = vm.get_vm_name()
        try:
            instance_id = self.get_instance_id_by_name(instance_name)

            # Terminate the instance
            self.client.terminate_instances(InstanceIds=[instance_id])
            print(f"VM '{instance_name}' is being terminated.") if print_output else None
            if db:
                db.delete_vm(vm)
        except ClientError as e:
            print(f"Failed to delete VM '{instance_name}': {e}")

    instance_type_to_hourly_rate = {
        't3.micro': 0.0084,  # Burstable performance (1 vCPU, 1 GB RAM)
        't3.small': 0.0168,  # Burstable performance (1 vCPU, 2 GB RAM)
        't3.medium': 0.0336,  # Burstable performance (2 vCPUs, 4 GB RAM)
        't3.large': 0.0672,  # Burstable performance (2 vCPUs, 8 GB RAM)
        't3.xlarge': 0.1344,  # Burstable performance (4 vCPUs, 16 GB RAM)
        't3.2xlarge': 0.2688,  # Burstable performance (8 vCPUs, 32 GB RAM)
        'm6g.medium': 0.0168,  # ARM-based (1 vCPU, 2 GB RAM)
        'm6g.large': 0.0336,  # ARM-based (2 vCPUs, 8 GB RAM)
        'm6g.xlarge': 0.0672,  # ARM-based (4 vCPUs, 16 GB RAM)
        'm6g.2xlarge': 0.1344,  # ARM-based (8 vCPUs, 32 GB RAM)
        'm5.large': 0.096,  # General purpose (2 vCPUs, 8 GB RAM)
        'm5.xlarge': 0.192,  # General purpose (4 vCPUs, 16 GB RAM)
        'm5.2xlarge': 0.384,  # General purpose (8 vCPUs, 32 GB RAM)
        'm5.4xlarge': 0.768,  # General purpose (16 vCPUs, 64 GB RAM)
        'm5.12xlarge': 2.304,  # General purpose (48 vCPUs, 192 GB RAM)
        'm5.24xlarge': 4.608,  # General purpose (96 vCPUs, 384 GB RAM)
        'c6g.medium': 0.0208,  # Compute optimized (1 vCPU, 2 GB RAM)
        'c6g.large': 0.0416,  # Compute optimized (2 vCPUs, 4 GB RAM)
        'c6g.xlarge': 0.0832,  # Compute optimized (4 vCPUs, 8 GB RAM)
        'c6g.2xlarge': 0.1664,  # Compute optimized (8 vCPUs, 16 GB RAM)
        'c5.large': 0.096,  # Compute optimized (2 vCPUs, 4 GB RAM)
        'c5.xlarge': 0.192,  # Compute optimized (4 vCPUs, 8 GB RAM)
        'c5.2xlarge': 0.384,  # Compute optimized (8 vCPUs, 16 GB RAM)
        'c5.4xlarge': 0.768,  # Compute optimized (16 vCPUs, 32 GB RAM)
        'c5.9xlarge': 1.728,  # Compute optimized (36 vCPUs, 72 GB RAM)
        'c5.18xlarge': 3.456,  # Compute optimized (72 vCPUs, 144 GB RAM)
        'r6g.medium': 0.0504,  # Memory optimized (1 vCPU, 8 GB RAM)
        'r6g.large': 0.1008,  # Memory optimized (2 vCPUs, 16 GB RAM)
        'r6g.xlarge': 0.2016,  # Memory optimized (4 vCPUs, 32 GB RAM)
        'r6g.2xlarge': 0.4032,  # Memory optimized (8 vCPUs, 64 GB RAM)
        'r5.large': 0.096,  # Memory optimized (2 vCPUs, 16 GB RAM)
        'r5.xlarge': 0.192,  # Memory optimized (4 vCPUs, 32 GB RAM)
        'r5.2xlarge': 0.384,  # Memory optimized (8 vCPUs, 64 GB RAM)
        'r5.12xlarge': 2.304,  # Memory optimized (48 vCPUs, 384 GB RAM)
        'r5.24xlarge': 4.608,  # Memory optimized (96 vCPUs, 768 GB RAM)
        'p3.2xlarge': 3.06,  # GPU-optimized (1 GPU, 8 vCPUs, 61 GB RAM)
        'p3.8xlarge': 12.24,  # GPU-optimized (4 GPUs, 32 vCPUs, 244 GB RAM)
        'p3.16xlarge': 24.48,  # GPU-optimized (8 GPUs, 64 vCPUs, 488 GB RAM)
        'g4ad.xlarge': 0.526,  # GPU-optimized (1 GPU, 4 vCPUs, 16 GB RAM)
        'g4ad.2xlarge': 1.052,  # GPU-optimized (1 GPU, 8 vCPUs, 32 GB RAM)
        'g4ad.4xlarge': 2.104,  # GPU-optimized (1 GPU, 16 vCPUs, 64 GB RAM)
        'g4dn.xlarge': 0.526,  # GPU-optimized (1 GPU, 4 vCPUs, 16 GB RAM)
        'g4dn.2xlarge': 1.052,  # GPU-optimized (1 GPU, 8 vCPUs, 32 GB RAM)
        'g4dn.4xlarge': 2.104,  # GPU-optimized (1 GPU, 16 vCPUs, 64 GB RAM)
        'g4dn.8xlarge': 4.208,  # GPU-optimized (1 GPU, 32 vCPUs, 128 GB RAM)
        'g4dn.16xlarge': 8.416,  # GPU-optimized (1 GPU, 64 vCPUs, 256 GB RAM)
        'inf1.xlarge': 0.256,  # Inference-optimized (4 vCPUs, 8 GB RAM)
        'inf1.2xlarge': 0.512,  # Inference-optimized (8 vCPUs, 16 GB RAM)
        'inf1.6xlarge': 1.024,  # Inference-optimized (24 vCPUs, 48 GB RAM)
        'inf1.24xlarge': 4.096,  # Inference-optimized (96 vCPUs, 192 GB RAM)
        'x1e.xlarge': 3.998,  # High memory (4 vCPUs, 122 GB RAM)
        'x1e.2xlarge': 7.996,  # High memory (8 vCPUs, 244 GB RAM)
        'x1e.4xlarge': 15.992,  # High memory (16 vCPUs, 488 GB RAM)
        'x1e.16xlarge': 63.968,  # High memory (64 vCPUs, 1952 GB RAM)
    }

    def get_vm_hourly_rate(self, vm: VirtualMachine, print_output=True) -> float:
        """
        Returns the hourly rate for an AWS VM, looking up the rate from a map.

        :param vm: The virtual machine for which the rate is requested.
        :param print_output: Flag to print the result to console.
        :return: Hourly rate for the VM.
        """
        # Get the instance name and retrieve its instance ID
        instance_name = vm.get_vm_name()
        instance_id = self.get_instance_id_by_name(instance_name)

        if not instance_id:
            print(f"VM '{instance_name}' not found.") if print_output else None
            return -1  # No instance found

        # Describe the instance using the AWS API to get its size
        try:
            response = self.client.describe_instances(InstanceIds=[instance_id])
            instance_type = response['Reservations'][0]['Instances'][0]['InstanceType']

            # Lookup the hourly rate from the predefined map
            hourly_rate = self.instance_type_to_hourly_rate.get(instance_type)

            if hourly_rate is None:
                print(f"Unable to find hourly rate for VM of type '{instance_type}' (VM: {instance_name})") if print_output else None
                return -1  # No rate found for the instance type

            return hourly_rate

        except ClientError as e:
            print(f"Error describing instance '{instance_name}': {e}")
            return -1

    def get_vm_uptime(self, vm: VirtualMachine, print_output=True):
        """
        Get the uptime of the EC2 VM.

        :param vm: VirtualMachine object whose uptime is to be calculated.
        :param print_output: Flag to print the result to console.
        :return: timedelta representing uptime of the VM.
        """
        try:
            # Get the instance ID by the VM name
            instance_id = self.get_instance_id_by_name(vm.get_vm_name())

            # Fetch instance info from AWS EC2
            instance_info = self.client.describe_instances(InstanceIds=[instance_id])['Reservations'][0]['Instances'][0]

            # Parse the launch time of the instance
            launch_time = instance_info['LaunchTime']

            # Ensure launch_time is timezone aware (AWS returns an aware datetime)
            launch_time_aware = launch_time.astimezone(pytz.utc)

            # Get current time as timezone-aware UTC datetime
            now_aware = datetime.now(pytz.utc)

            # Calculate uptime (both times are aware)
            uptime_timedelta = now_aware - launch_time_aware

            if print_output:
                print(f"Uptime for VM '{vm.get_vm_name()}': {uptime_timedelta}.")

            return uptime_timedelta  # Return the timedelta object

        except Exception as e:
            if print_output:
                print(f"Failed to calculate uptime for VM '{vm.get_vm_name()}': {e}")
            return None

    def get_vm_cost(self, vm: VirtualMachine, print_output=True) -> float:
        """
        Calculates the total cost of an AWS EC2 instance based on uptime and hourly rate.

        Args:
            vm (VirtualMachine): The virtual machine to calculate cost for.
            print_output (bool): Whether to print the cost.

        Returns:
            float: Total cost in USD.
        """
        try:
            # Retrieve the instance ID from the VM
            instance_name = vm.get_vm_name()
            instance_id = self.get_instance_id_by_name(instance_name)

            if not instance_id:
                if print_output:
                    print(f"Failed to find instance ID for '{instance_name}'.")
                return 0.0

            # Describe the instance to get its details (like instance type)
            instance_info = self.client.describe_instances(InstanceIds=[instance_id])['Reservations'][0]['Instances'][0]
            instance_type = instance_info['InstanceType']  # Retrieve the instance type

            # Calculate uptime as timedelta and convert it to hours
            uptime_timedelta = self.get_vm_uptime(vm, print_output=False)
            if uptime_timedelta is None:
                return 0.0

            uptime_hours = uptime_timedelta.total_seconds() / 3600  # Convert to hours

            # Retrieve hourly rate for the instance type
            hourly_rate = self.get_vm_hourly_rate(vm, print_output=False)

            # Calculate total cost
            total_cost = uptime_hours * hourly_rate

            if print_output:
                print(
                    f"Total cost for VM '{vm.get_vm_name()}' (instance type: {instance_type}): ${total_cost:.4f} USD.")

            return total_cost

        except Exception as e:
            if print_output:
                print(f"Failed to calculate total cost for VM '{vm.get_vm_name()}': {e}")
            return 0.0

    def get_instance_id_by_name(self, instance_name: str, print_output=True):
        """Gets the instance ID of an EC2 instance by its name, ignoring terminated instances."""
        try:
            response = self.client.describe_instances(
                Filters=[{'Name': 'tag:Name', 'Values': [instance_name]}]
            )

            # Go through each reservation and check the instances
            for reservation in response['Reservations']:
                for instance in reservation['Instances']:
                    state = instance['State']['Name']

                    if state != 'terminated':
                        # Return the instance ID of the non-terminated instance
                        return instance['InstanceId']

            print(f"No active instance found with name '{instance_name}'.") if print_output else None
            return None

        except ClientError as e:
            print(f"Failed to get instance ID for '{instance_name}': {e}")
            return None

    def is_active(self, vm: VirtualMachine) -> bool:
        """
        Checks if the VM is currently running on AWS.

        :param vm: The virtual machine to check.
        :return: True if the VM is running, False otherwise.
        """
        instance_name = vm.get_vm_name()

        try:
            # Get the instance ID by the VM name
            instance_id = self.get_instance_id_by_name(instance_name)

            # Fetch instance info from AWS EC2
            instance_info = self.client.describe_instances(InstanceIds=[instance_id])['Reservations'][0]['Instances'][0]

            # Get the current state of the instance
            state = instance_info['State']['Name']

            # Return True if the instance is running, False otherwise
            if state == 'running':
                return True
            else:
                return False

        except ClientError as e:
            print(f"Failed to check the status of VM '{instance_name}': {e}")
            return False

    def __str__(self):
        return f"\n AWS Provider:\n" \
               f" Account Name: {self.get_account_name()}\n" \
               f" Connection Date: {self.get_connection_date()}\n" \
               f" Access Key: {self.access_key}\n" \
               f" Secret Key: {self.secret_key}\n" \
               f" Region: {self.region}\n" \
               f" VPC ID: {self.vpc_id}\n" \
               f" Subnet ID: {self.subnet_id}\n" \
               f" Security Group ID: {self.security_group_id}\n"
