import time
import boto3
from botocore.exceptions import ClientError
from datetime import date
from vm import VirtualMachine, Provider

class AWS(Provider):
    """AWS cloud provider implementation."""

    def __init__(self, account_name: str, connection_date: date, access_key: str, secret_key: str, region: str, vpc_id: str = None, subnet_id: str = None, security_group_id: str = None):
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
        access_key, secret_key, region, vpc_id, subnet_id, security_group_id = provider_info.split(Provider.starting_character)[1].split(Provider.delimiter)
        return AWS(account_name, connection_date, access_key, secret_key, region, vpc_id, subnet_id, security_group_id)

    def get_provider_name(self) -> str:
        """Returns the name of the provider (AWS)."""
        return "AWS"

    def get_provider_info(self) -> str:
        """Returns information about the provider."""
        return self.get_provider_name() + self.starting_character + f"{self.access_key}{Provider.delimiter}{self.secret_key}{Provider.delimiter}{self.region}{Provider.delimiter}{self.vpc_id}{Provider.delimiter}{self.subnet_id}{Provider.delimiter}{self.security_group_id}"

    def connection_is_alive(self) -> bool:
        """Verifies if AWS credentials and connection work."""
        try:
            self.client.describe_regions()
            print("Authenticated successfully.")
            return True
        except ClientError as e:
            print(f"Authentication failed: {e}")
            return False

    def create_resources(self, location: str):
        """Creates VPC, subnet, security group only if not already created."""
        try:
            if self.vpc_id is None:
                # Create a VPC
                vpc = self.client.create_vpc(CidrBlock='10.0.0.0/16')
                self.vpc_id = vpc['Vpc']['VpcId']
                print(f"Created VPC with ID {self.vpc_id}")

                # Create an Internet Gateway and attach it to the VPC
                internet_gateway = self.client.create_internet_gateway()
                internet_gateway_id = internet_gateway['InternetGateway']['InternetGatewayId']
                self.client.attach_internet_gateway(VpcId=self.vpc_id, InternetGatewayId=internet_gateway_id)
                print(f"Created and attached Internet Gateway {internet_gateway_id} to VPC")

                # Create a public subnet
                subnet = self.client.create_subnet(
                    VpcId=self.vpc_id, CidrBlock='10.0.1.0/24', AvailabilityZone=location+'a')

                # Enable auto-assign public IP feature after subnet creation
                self.client.modify_subnet_attribute(
                    SubnetId=subnet['Subnet']['SubnetId'],
                    MapPublicIpOnLaunch={'Value': True}  # Enables auto-assigning of public IPs
                )

                self.subnet_id = subnet['Subnet']['SubnetId']
                print(f"Created public subnet {self.subnet_id}")

                # Create a Route Table and associate it with the subnet (so it can access the Internet Gateway)
                route_table = self.client.create_route_table(VpcId=self.vpc_id)
                route_table_id = route_table['RouteTable']['RouteTableId']
                self.client.create_route(
                    RouteTableId=route_table_id,
                    DestinationCidrBlock='0.0.0.0/0',
                    GatewayId=internet_gateway_id
                )
                self.client.associate_route_table(RouteTableId=route_table_id, SubnetId=self.subnet_id)
                print("Set up routing for subnet to access the internet via the gateway.")

                # Create a Security Group with no restrictions (open to all traffic)
                security_group = self.client.create_security_group(
                    GroupName='AllowAllTraffic', Description='Allow all inbound/outbound traffic', VpcId=self.vpc_id)
                self.security_group_id = security_group['GroupId']
                self.client.authorize_security_group_ingress(
                    GroupId=self.security_group_id,
                    IpProtocol='-1',  # Allow all traffic
                    CidrIp='0.0.0.0/0'
                )
                print(f"Security Group {self.security_group_id} created allowing all inbound/outbound traffic.")

        except ClientError as e:
            print(f"Failed to create resources: {e}")

    def create_vm(self, location: str, vm_name: str, vm_size: str, admin_password: str, image_reference: str,
                  ssh_key_name: str, max_retries: int = 1000, retry_interval: int = 10):
        """Creates an EC2 instance on AWS with public access (reachable from the internet)."""
        try:
            # Make sure resources are created if not already done
            if self.vpc_id is None or self.subnet_id is None or self.security_group_id is None:
                self.create_resources(location)

            print(self.vpc_id + " " + self.subnet_id + " " + self.security_group_id)

            # EC2 instance configuration
            params = {
                "ImageId": image_reference,
                "InstanceType": vm_size,
                "KeyName": ssh_key_name,
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

            print(f"VM '{vm_name}' is being created...")
            instance = self.client.run_instances(**params)['Instances'][0]

            instance_id = instance['InstanceId']
            print(f"VM '{vm_name}' created. Instance ID: {instance_id}")

            # Wait for the instance to be running
            retries = 0
            public_ip = None
            while retries < max_retries:
                instance_info = self.client.describe_instances(InstanceIds=[instance_id])['Reservations'][0]['Instances'][0]
                state = instance_info['State']['Name']

                if state == 'running':
                    public_ip = instance_info.get('PublicIpAddress', "Pending")
                    print(f"Instance '{vm_name}' is running. Public IP: {public_ip}")
                    break
                else:
                    print(f"Instance '{vm_name}' state: {state}")

                retries += 1
                time.sleep(retry_interval)

            if not public_ip:
                print(f"Failed to get public IP for instance '{vm_name}' after {max_retries} retries.")
                return None

            # Return the VirtualMachine object
            return VirtualMachine(
                vm_name,
                self,
                True,
                False,
                2000000,  # Adjust this based on AWS pricing
                public_ip or "Pending",
                date.today(),
                "ec2-user",  # Default AWS username
                admin_password,
                "",
                ssh_key_name
            )

        except ClientError as e:
            print(f"Failed to create VM '{vm_name}': {e}")
            return None

    def stop_vm(self, vm: VirtualMachine):
        """Stops an EC2 instance on AWS."""
        try:
            instance_name = vm.get_vm_name()

            # Get the instance ID by the instance name
            instance_id = self.get_instance_id_by_name(instance_name)

            # Stop the instance using the instance ID
            self.client.stop_instances(InstanceIds=[instance_id])
            vm.set_is_active(False)
            print(f"Stopping VM '{instance_name}' (ID: {instance_id}).")

        except ClientError as e:
            print(f"Failed to stop VM '{instance_name}': {e}")



    def start_vm(self, vm: VirtualMachine):
        """Stops an EC2 instance on AWS."""
        try:
            instance_name = vm.get_vm_name()

            # Get the instance ID by the instance name
            instance_id = self.get_instance_id_by_name(instance_name)

            # Stop the instance using the instance ID
            self.client.start_instances(InstanceIds=[instance_id])
            vm.set_is_active(True)
            print(f"Starting VM '{instance_name}' (ID: {instance_id}).")

        except ClientError as e:
            print(f"Failed to start VM '{instance_name}': {e}")

    import time

    def delete_vm(self, vm: VirtualMachine):
        """Deletes an EC2 instance on AWS."""
        try:
            instance_name = vm.get_vm_name()
            instance_id = self.get_instance_id_by_name(instance_name)

            # Terminate the instance
            self.client.terminate_instances(InstanceIds=[instance_id])
            print(f"VM '{instance_name}' is being terminated.")

        except ClientError as e:
            print(f"Failed to delete VM '{instance_name}': {e}")

    def get_instance_id_by_name(self, instance_name: str):
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

            print(f"No active instance found with name '{instance_name}'.")
            return None

        except ClientError as e:
            print(f"Failed to get instance ID for '{instance_name}': {e}")
            return None

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