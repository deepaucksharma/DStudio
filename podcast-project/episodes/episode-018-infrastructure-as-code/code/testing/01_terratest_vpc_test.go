// Example 7: Terratest Infrastructure Testing
// यह example Terraform infrastructure को automatically test करता है
// Flipkart infrastructure की reliability ensure करने के लिए

package test

import (
	"fmt"
	"net"
	"testing"
	"time"

	"github.com/aws/aws-sdk-go/aws"
	"github.com/aws/aws-sdk-go/aws/session"
	"github.com/aws/aws-sdk-go/service/ec2"
	"github.com/gruntwork-io/terratest/modules/terraform"
	"github.com/gruntwork-io/terratest/modules/test-structure"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

// TestFlipkartVPCInfrastructure tests the complete VPC infrastructure
func TestFlipkartVPCInfrastructure(t *testing.T) {
	t.Parallel()

	// Setup test directory
	workingDir := "../terraform"
	
	// Defer cleanup to ensure resources are destroyed
	defer test_structure.RunTestStage(t, "cleanup", func() {
		terraformOptions := test_structure.LoadTerraformOptions(t, workingDir)
		terraform.Destroy(t, terraformOptions)
	})

	test_structure.RunTestStage(t, "setup", func() {
		terraformOptions := configureTerraformOptions(t, workingDir)
		test_structure.SaveTerraformOptions(t, workingDir, terraformOptions)
		
		// Initialize and apply Terraform
		terraform.InitAndApply(t, terraformOptions)
	})

	test_structure.RunTestStage(t, "validate", func() {
		terraformOptions := test_structure.LoadTerraformOptions(t, workingDir)
		validateVPCInfrastructure(t, terraformOptions)
	})
}

// configureTerraformOptions configures Terraform options for testing
func configureTerraformOptions(t *testing.T, workingDir string) *terraform.Options {
	// Generate unique identifier for test resources
	uniqueID := fmt.Sprintf("terratest-%d", time.Now().Unix())
	
	return &terraform.Options{
		// Path to Terraform configuration
		TerraformDir: workingDir,
		
		// Variables to pass to Terraform
		Vars: map[string]interface{}{
			"environment_name": fmt.Sprintf("test-%s", uniqueID),
			"region":          "ap-south-1", // Mumbai region
		},
		
		// Environment variables
		EnvVars: map[string]string{
			"AWS_DEFAULT_REGION": "ap-south-1",
		},
		
		// Retry configuration for flaky tests
		RetryableTerraformErrors: map[string]string{
			".*": "Failed to create.*",
		},
		MaxRetries:         3,
		TimeBetweenRetries: 5 * time.Second,
		
		// Disable color output for CI/CD
		NoColor: true,
	}
}

// validateVPCInfrastructure validates that VPC infrastructure is correctly set up
func validateVPCInfrastructure(t *testing.T, terraformOptions *terraform.Options) {
	// Get outputs from Terraform
	vpcID := terraform.Output(t, terraformOptions, "vpc_id")
	publicSubnetIDs := terraform.OutputList(t, terraformOptions, "public_subnet_ids")
	privateSubnetIDs := terraform.OutputList(t, terraformOptions, "private_subnet_ids")
	databaseSubnetIDs := terraform.OutputList(t, terraformOptions, "database_subnet_ids")

	// Validate VPC exists and has correct configuration
	t.Run("VPC Configuration", func(t *testing.T) {
		validateVPC(t, vpcID)
	})

	// Validate public subnets
	t.Run("Public Subnets", func(t *testing.T) {
		validatePublicSubnets(t, vpcID, publicSubnetIDs)
	})

	// Validate private subnets
	t.Run("Private Subnets", func(t *testing.T) {
		validatePrivateSubnets(t, vpcID, privateSubnetIDs)
	})

	// Validate database subnets
	t.Run("Database Subnets", func(t *testing.T) {
		validateDatabaseSubnets(t, vpcID, databaseSubnetIDs)
	})

	// Validate internet connectivity
	t.Run("Internet Connectivity", func(t *testing.T) {
		validateInternetConnectivity(t, vpcID)
	})

	// Validate security groups
	t.Run("Security Groups", func(t *testing.T) {
		validateSecurityGroups(t, vpcID)
	})
}

// validateVPC validates VPC configuration
func validateVPC(t *testing.T, vpcID string) {
	// Create AWS session
	sess := createAWSSession(t)
	ec2Client := ec2.New(sess)

	// Describe VPC
	result, err := ec2Client.DescribeVpcs(&ec2.DescribeVpcsInput{
		VpcIds: []*string{aws.String(vpcID)},
	})
	require.NoError(t, err)
	require.Len(t, result.Vpcs, 1)

	vpc := result.Vpcs[0]

	// Validate VPC CIDR block
	assert.Equal(t, "10.0.0.0/16", *vpc.CidrBlock)

	// Validate DNS support is enabled
	assert.True(t, *vpc.EnableDnsSupport)
	assert.True(t, *vpc.EnableDnsHostnames)

	// Validate VPC state
	assert.Equal(t, "available", *vpc.State)

	// Validate tags
	validateTags(t, vpc.Tags, map[string]string{
		"Environment": "test",
		"Project":     "flipkart-infrastructure",
		"ManagedBy":   "terraform",
	})

	fmt.Printf("✅ VPC %s validated successfully\n", vpcID)
}

// validatePublicSubnets validates public subnet configuration
func validatePublicSubnets(t *testing.T, vpcID string, subnetIDs []string) {
	sess := createAWSSession(t)
	ec2Client := ec2.New(sess)

	// Should have 3 public subnets for high availability
	assert.Len(t, subnetIDs, 3)

	for i, subnetID := range subnetIDs {
		// Describe subnet
		result, err := ec2Client.DescribeSubnets(&ec2.DescribeSubnetsInput{
			SubnetIds: []*string{aws.String(subnetID)},
		})
		require.NoError(t, err)
		require.Len(t, result.Subnets, 1)

		subnet := result.Subnets[0]

		// Validate subnet belongs to correct VPC
		assert.Equal(t, vpcID, *subnet.VpcId)

		// Validate public IP assignment
		assert.True(t, *subnet.MapPublicIpOnLaunch)

		// Validate subnet state
		assert.Equal(t, "available", *subnet.State)

		// Validate CIDR blocks are in expected range
		expectedCIDR := fmt.Sprintf("10.0.%d.0/24", i+1)
		assert.Equal(t, expectedCIDR, *subnet.CidrBlock)

		// Validate subnet is in different AZ
		assert.NotEmpty(t, *subnet.AvailabilityZone)

		fmt.Printf("✅ Public Subnet %s validated successfully in AZ %s\n", 
			subnetID, *subnet.AvailabilityZone)
	}

	// Validate subnets are in different availability zones
	validateSubnetsInDifferentAZs(t, ec2Client, subnetIDs)
}

// validatePrivateSubnets validates private subnet configuration
func validatePrivateSubnets(t *testing.T, vpcID string, subnetIDs []string) {
	sess := createAWSSession(t)
	ec2Client := ec2.New(sess)

	// Should have 3 private subnets
	assert.Len(t, subnetIDs, 3)

	for i, subnetID := range subnetIDs {
		result, err := ec2Client.DescribeSubnets(&ec2.DescribeSubnetsInput{
			SubnetIds: []*string{aws.String(subnetID)},
		})
		require.NoError(t, err)
		require.Len(t, result.Subnets, 1)

		subnet := result.Subnets[0]

		// Validate subnet belongs to correct VPC
		assert.Equal(t, vpcID, *subnet.VpcId)

		// Validate NO public IP assignment for private subnets
		assert.False(t, *subnet.MapPublicIpOnLaunch)

		// Validate CIDR blocks are in expected range
		expectedCIDR := fmt.Sprintf("10.0.%d.0/24", i+10)
		assert.Equal(t, expectedCIDR, *subnet.CidrBlock)

		fmt.Printf("✅ Private Subnet %s validated successfully\n", subnetID)
	}
}

// validateDatabaseSubnets validates database subnet configuration
func validateDatabaseSubnets(t *testing.T, vpcID string, subnetIDs []string) {
	sess := createAWSSession(t)
	ec2Client := ec2.New(sess)

	// Should have 3 database subnets
	assert.Len(t, subnetIDs, 3)

	for i, subnetID := range subnetIDs {
		result, err := ec2Client.DescribeSubnets(&ec2.DescribeSubnetsInput{
			SubnetIds: []*string{aws.String(subnetID)},
		})
		require.NoError(t, err)
		require.Len(t, result.Subnets, 1)

		subnet := result.Subnets[0]

		// Validate subnet belongs to correct VPC
		assert.Equal(t, vpcID, *subnet.VpcId)

		// Validate NO public IP assignment for database subnets
		assert.False(t, *subnet.MapPublicIpOnLaunch)

		// Validate CIDR blocks are in expected range (20-22)
		expectedCIDR := fmt.Sprintf("10.0.%d.0/24", i+20)
		assert.Equal(t, expectedCIDR, *subnet.CidrBlock)

		fmt.Printf("✅ Database Subnet %s validated successfully\n", subnetID)
	}
}

// validateInternetConnectivity validates internet gateway and routing
func validateInternetConnectivity(t *testing.T, vpcID string) {
	sess := createAWSSession(t)
	ec2Client := ec2.New(sess)

	// Check for Internet Gateway
	igwResult, err := ec2Client.DescribeInternetGateways(&ec2.DescribeInternetGatewaysInput{
		Filters: []*ec2.Filter{
			{
				Name:   aws.String("attachment.vpc-id"),
				Values: []*string{aws.String(vpcID)},
			},
		},
	})
	require.NoError(t, err)
	require.Len(t, igwResult.InternetGateways, 1)

	igw := igwResult.InternetGateways[0]
	assert.Equal(t, "available", *igw.Attachments[0].State)

	fmt.Printf("✅ Internet Gateway %s validated successfully\n", *igw.InternetGatewayId)

	// Check for NAT Gateways
	natResult, err := ec2Client.DescribeNatGateways(&ec2.DescribeNatGatewaysInput{
		Filter: []*ec2.Filter{
			{
				Name:   aws.String("vpc-id"),
				Values: []*string{aws.String(vpcID)},
			},
		},
	})
	require.NoError(t, err)
	assert.GreaterOrEqual(t, len(natResult.NatGateways), 1)

	for _, natGw := range natResult.NatGateways {
		assert.Equal(t, "available", *natGw.State)
		fmt.Printf("✅ NAT Gateway %s validated successfully\n", *natGw.NatGatewayId)
	}
}

// validateSecurityGroups validates security group configuration
func validateSecurityGroups(t *testing.T, vpcID string) {
	sess := createAWSSession(t)
	ec2Client := ec2.New(sess)

	// Get security groups for the VPC
	result, err := ec2Client.DescribeSecurityGroups(&ec2.DescribeSecurityGroupsInput{
		Filters: []*ec2.Filter{
			{
				Name:   aws.String("vpc-id"),
				Values: []*string{aws.String(vpcID)},
			},
		},
	})
	require.NoError(t, err)

	// Should have at least default security group
	assert.GreaterOrEqual(t, len(result.SecurityGroups), 1)

	for _, sg := range result.SecurityGroups {
		// Validate security group belongs to correct VPC
		assert.Equal(t, vpcID, *sg.VpcId)

		// Log security group rules for verification
		fmt.Printf("Security Group %s (%s) has %d ingress and %d egress rules\n",
			*sg.GroupId, *sg.GroupName,
			len(sg.IpPermissions), len(sg.IpPermissionsEgress))
	}
}

// validateSubnetsInDifferentAZs ensures subnets are distributed across AZs
func validateSubnetsInDifferentAZs(t *testing.T, ec2Client *ec2.EC2, subnetIDs []string) {
	azMap := make(map[string]bool)

	for _, subnetID := range subnetIDs {
		result, err := ec2Client.DescribeSubnets(&ec2.DescribeSubnetsInput{
			SubnetIds: []*string{aws.String(subnetID)},
		})
		require.NoError(t, err)
		require.Len(t, result.Subnets, 1)

		az := *result.Subnets[0].AvailabilityZone
		azMap[az] = true
	}

	// Ensure subnets are in different AZs for high availability
	assert.Equal(t, len(subnetIDs), len(azMap), 
		"Subnets should be distributed across different availability zones")

	fmt.Printf("✅ Subnets distributed across %d availability zones\n", len(azMap))
}

// validateTags validates that required tags are present
func validateTags(t *testing.T, tags []*ec2.Tag, expectedTags map[string]string) {
	tagMap := make(map[string]string)
	for _, tag := range tags {
		tagMap[*tag.Key] = *tag.Value
	}

	for key, expectedValue := range expectedTags {
		actualValue, exists := tagMap[key]
		assert.True(t, exists, "Tag %s should exist", key)
		if exists {
			assert.Contains(t, actualValue, expectedValue, 
				"Tag %s should contain %s", key, expectedValue)
		}
	}
}

// createAWSSession creates an AWS session for testing
func createAWSSession(t *testing.T) *session.Session {
	sess, err := session.NewSession(&aws.Config{
		Region: aws.String("ap-south-1"), // Mumbai region
	})
	require.NoError(t, err)
	return sess
}

// Additional helper functions

// TestNetworkConnectivity tests actual network connectivity
func TestNetworkConnectivity(t *testing.T) {
	t.Parallel()

	// Test that we can resolve DNS
	_, err := net.LookupHost("aws.amazon.com")
	assert.NoError(t, err, "Should be able to resolve external DNS")

	// Test specific ports if needed
	conn, err := net.DialTimeout("tcp", "aws.amazon.com:443", 5*time.Second)
	if err == nil {
		conn.Close()
	}
	assert.NoError(t, err, "Should be able to connect to HTTPS port")
}

// TestCostOptimization validates cost optimization measures
func TestCostOptimization(t *testing.T) {
	t.Parallel()

	workingDir := "../terraform"
	terraformOptions := test_structure.LoadTerraformOptions(t, workingDir)

	// Check NAT Gateway count for cost optimization
	natGateways := terraform.OutputList(t, terraformOptions, "nat_gateway_ids")
	
	// In test environment, we might use fewer NAT Gateways for cost savings
	assert.LessOrEqual(t, len(natGateways), 3, 
		"Should not have more than 3 NAT Gateways")

	// If only 1 NAT Gateway, log cost optimization note
	if len(natGateways) == 1 {
		fmt.Println("💰 Cost optimization: Using single NAT Gateway")
	}
}

// TestSecurityCompliance validates security compliance
func TestSecurityCompliance(t *testing.T) {
	t.Parallel()

	workingDir := "../terraform"
	terraformOptions := test_structure.LoadTerraformOptions(t, workingDir)

	vpcID := terraform.Output(t, terraformOptions, "vpc_id")
	sess := createAWSSession(t)
	ec2Client := ec2.New(sess)

	// Validate that no security groups allow unrestricted SSH access
	result, err := ec2Client.DescribeSecurityGroups(&ec2.DescribeSecurityGroupsInput{
		Filters: []*ec2.Filter{
			{
				Name:   aws.String("vpc-id"),
				Values: []*string{aws.String(vpcID)},
			},
		},
	})
	require.NoError(t, err)

	for _, sg := range result.SecurityGroups {
		for _, rule := range sg.IpPermissions {
			if rule.FromPort != nil && *rule.FromPort == 22 {
				for _, ipRange := range rule.IpRanges {
					assert.NotEqual(t, "0.0.0.0/0", *ipRange.CidrIp,
						"Security group %s should not allow SSH from anywhere", *sg.GroupId)
				}
			}
		}
	}

	fmt.Println("🔒 Security compliance validated")
}

// Benchmark test for infrastructure provisioning time
func BenchmarkInfrastructureProvisioning(b *testing.B) {
	workingDir := "../terraform"
	
	for i := 0; i < b.N; i++ {
		b.StopTimer()
		
		uniqueID := fmt.Sprintf("bench-%d-%d", time.Now().Unix(), i)
		terraformOptions := &terraform.Options{
			TerraformDir: workingDir,
			Vars: map[string]interface{}{
				"environment_name": uniqueID,
			},
			NoColor: true,
		}
		
		b.StartTimer()
		
		// Measure time to provision infrastructure
		terraform.InitAndApply(b, terraformOptions)
		
		b.StopTimer()
		
		// Cleanup
		terraform.Destroy(b, terraformOptions)
	}
}