// Semantic Versioning Manager
// सेमेंटिक वर्जनिंग मैनेजर
//
// Real-world example: Razorpay API versioning system
// Handles semantic version comparison, compatibility checking, and migration guidance

package main

import (
	"encoding/json"
	"fmt"
	"log"
	"regexp"
	"sort"
	"strconv"
	"strings"
	"time"
)

// Version represents a semantic version
// वर्जन एक सेमेंटिक वर्जन को दर्शाता है
type Version struct {
	Major      int       `json:"major"`
	Minor      int       `json:"minor"`
	Patch      int       `json:"patch"`
	PreRelease string    `json:"pre_release,omitempty"`
	Build      string    `json:"build,omitempty"`
	ReleaseDate time.Time `json:"release_date"`
}

// VersionMetadata contains version information
// वर्जन मेटाडेटा में वर्जन की जानकारी होती है
type VersionMetadata struct {
	Version     Version             `json:"version"`
	Description string              `json:"description"`
	Status      string              `json:"status"` // active, deprecated, sunset
	Deprecated  *time.Time          `json:"deprecated_at,omitempty"`
	SunsetDate  *time.Time          `json:"sunset_at,omitempty"`
	Changes     []ChangelogEntry    `json:"changes"`
	Migration   MigrationGuide      `json:"migration"`
	Dependencies map[string]string  `json:"dependencies"`
}

// ChangelogEntry represents a single change
type ChangelogEntry struct {
	Type        string `json:"type"` // feature, fix, breaking, security
	Description string `json:"description"`
	Impact      string `json:"impact"` // low, medium, high, critical
}

// MigrationGuide provides migration information
type MigrationGuide struct {
	FromVersion   string            `json:"from_version"`
	ToVersion     string            `json:"to_version"`
	Steps         []string          `json:"steps"`
	AutoMigration bool              `json:"auto_migration"`
	CodeExamples  map[string]string `json:"code_examples"`
}

// CompatibilityLevel defines compatibility types
type CompatibilityLevel int

const (
	Incompatible CompatibilityLevel = iota
	BackwardCompatible
	ForwardCompatible
	FullyCompatible
)

// RazorpayVersionManager manages API versions for Razorpay-style system
// रेज़रपे वर्जन मैनेजर Razorpay-स्टाइल सिस्टम के लिए API वर्जन मैनेज करता है
type RazorpayVersionManager struct {
	versions       map[string]VersionMetadata
	defaultVersion string
	currentVersion string
	versionRegex   *regexp.Regexp
}

// NewRazorpayVersionManager creates a new version manager
func NewRazorpayVersionManager() *RazorpayVersionManager {
	vm := &RazorpayVersionManager{
		versions:       make(map[string]VersionMetadata),
		defaultVersion: "2.1.0",
		currentVersion: "2.1.0",
		versionRegex:   regexp.MustCompile(`^(\d+)\.(\d+)\.(\d+)(?:-([a-zA-Z0-9-]+))?(?:\+([a-zA-Z0-9-]+))?$`),
	}
	
	vm.initializeVersions()
	return vm
}

// initializeVersions sets up initial versions
// प्रारंभिक वर्जन सेट करता है
func (vm *RazorpayVersionManager) initializeVersions() {
	fmt.Println("🔧 Initializing Razorpay API versions...")
	
	// Version 1.0.0 - Legacy Payment Gateway
	v1 := VersionMetadata{
		Version: Version{
			Major:       1,
			Minor:       0,
			Patch:       0,
			ReleaseDate: time.Date(2020, 1, 1, 0, 0, 0, 0, time.UTC),
		},
		Description: "Legacy payment gateway API - लेगेसी पेमेंट गेटवे API",
		Status:      "deprecated",
		Changes: []ChangelogEntry{
			{Type: "feature", Description: "Basic payment processing", Impact: "medium"},
			{Type: "feature", Description: "Card payments support", Impact: "high"},
		},
		Migration: MigrationGuide{
			FromVersion:   "1.0.0",
			ToVersion:     "2.0.0",
			AutoMigration: false,
			Steps: []string{
				"Update API endpoints from /v1/ to /v2/",
				"Replace card_token with payment_method_id",
				"Update webhook payload structure",
			},
		},
	}
	
	deprecationDate := time.Date(2023, 6, 1, 0, 0, 0, 0, time.UTC)
	v1.Deprecated = &deprecationDate
	
	vm.versions["1.0.0"] = v1
	
	// Version 2.0.0 - Enhanced with UPI
	v2 := VersionMetadata{
		Version: Version{
			Major:       2,
			Minor:       0,
			Patch:       0,
			ReleaseDate: time.Date(2022, 6, 1, 0, 0, 0, 0, time.UTC),
		},
		Description: "Enhanced API with UPI support - UPI सपोर्ट के साथ एन्हांस्ड API",
		Status:      "active",
		Changes: []ChangelogEntry{
			{Type: "feature", Description: "UPI payments support", Impact: "high"},
			{Type: "feature", Description: "Enhanced fraud detection", Impact: "medium"},
			{Type: "breaking", Description: "Changed webhook payload structure", Impact: "high"},
		},
		Migration: MigrationGuide{
			FromVersion:   "1.0.0",
			ToVersion:     "2.0.0",
			AutoMigration: false,
			Steps: []string{
				"Migrate to new webhook payload format",
				"Update UPI payment flow integration",
				"Test new fraud detection responses",
			},
		},
	}
	
	vm.versions["2.0.0"] = v2
	
	// Version 2.1.0 - Current stable with BNPL
	v21 := VersionMetadata{
		Version: Version{
			Major:       2,
			Minor:       1,
			Patch:       0,
			ReleaseDate: time.Date(2024, 1, 15, 0, 0, 0, 0, time.UTC),
		},
		Description: "Current stable with BNPL - BNPL के साथ करंट स्टेबल",
		Status:      "active",
		Changes: []ChangelogEntry{
			{Type: "feature", Description: "Buy Now Pay Later (BNPL) integration", Impact: "high"},
			{Type: "feature", Description: "Enhanced analytics and reporting", Impact: "medium"},
			{Type: "fix", Description: "Improved error handling for failed transactions", Impact: "medium"},
		},
		Migration: MigrationGuide{
			FromVersion:   "2.0.0",
			ToVersion:     "2.1.0",
			AutoMigration: true,
			Steps: []string{
				"No breaking changes - automatic migration",
				"Optional: Enable BNPL features in dashboard",
				"Update SDK to latest version for new features",
			},
		},
		Dependencies: map[string]string{
			"fraud-service": ">=3.2.0",
			"upi-service":   ">=2.1.0",
			"bnpl-service":  ">=1.0.0",
		},
	}
	
	vm.versions["2.1.0"] = v21
	
	// Version 3.0.0-beta - Future with CBDC
	v3 := VersionMetadata{
		Version: Version{
			Major:      3,
			Minor:      0,
			Patch:      0,
			PreRelease: "beta",
			ReleaseDate: time.Date(2024, 8, 1, 0, 0, 0, 0, time.UTC),
		},
		Description: "Beta with CBDC support - CBDC सपोर्ट के साथ बीटा",
		Status:      "beta",
		Changes: []ChangelogEntry{
			{Type: "feature", Description: "Central Bank Digital Currency (CBDC) support", Impact: "critical"},
			{Type: "feature", Description: "Cross-border payment capabilities", Impact: "high"},
			{Type: "breaking", Description: "New authentication mechanism", Impact: "critical"},
		},
		Migration: MigrationGuide{
			FromVersion:   "2.1.0",
			ToVersion:     "3.0.0",
			AutoMigration: false,
			Steps: []string{
				"Update authentication to OAuth 2.1",
				"Integrate CBDC payment methods",
				"Test cross-border payment flows",
				"Update compliance for digital rupee transactions",
			},
		},
	}
	
	vm.versions["3.0.0-beta"] = v3
}

// ParseVersion parses a version string into Version struct
// वर्जन स्ट्रिंग को Version struct में पार्स करता है
func (vm *RazorpayVersionManager) ParseVersion(versionStr string) (*Version, error) {
	matches := vm.versionRegex.FindStringSubmatch(versionStr)
	if matches == nil {
		return nil, fmt.Errorf("invalid version format: %s", versionStr)
	}
	
	major, _ := strconv.Atoi(matches[1])
	minor, _ := strconv.Atoi(matches[2])
	patch, _ := strconv.Atoi(matches[3])
	
	version := &Version{
		Major: major,
		Minor: minor,
		Patch: patch,
	}
	
	if len(matches) > 4 && matches[4] != "" {
		version.PreRelease = matches[4]
	}
	
	if len(matches) > 5 && matches[5] != "" {
		version.Build = matches[5]
	}
	
	return version, nil
}

// CompareVersions compares two versions
// दो वर्जन की तुलना करता है
func (vm *RazorpayVersionManager) CompareVersions(v1, v2 string) (int, error) {
	version1, err := vm.ParseVersion(v1)
	if err != nil {
		return 0, err
	}
	
	version2, err := vm.ParseVersion(v2)
	if err != nil {
		return 0, err
	}
	
	// Compare major
	if version1.Major != version2.Major {
		if version1.Major > version2.Major {
			return 1, nil
		}
		return -1, nil
	}
	
	// Compare minor
	if version1.Minor != version2.Minor {
		if version1.Minor > version2.Minor {
			return 1, nil
		}
		return -1, nil
	}
	
	// Compare patch
	if version1.Patch != version2.Patch {
		if version1.Patch > version2.Patch {
			return 1, nil
		}
		return -1, nil
	}
	
	// Compare pre-release (simplified)
	if version1.PreRelease == "" && version2.PreRelease != "" {
		return 1, nil // Release > pre-release
	}
	if version1.PreRelease != "" && version2.PreRelease == "" {
		return -1, nil // Pre-release < release
	}
	
	return 0, nil // Equal
}

// GetCompatibilityLevel determines compatibility between versions
// वर्जन के बीच compatibility level निर्धारित करता है
func (vm *RazorpayVersionManager) GetCompatibilityLevel(from, to string) (CompatibilityLevel, error) {
	v1, err := vm.ParseVersion(from)
	if err != nil {
		return Incompatible, err
	}
	
	v2, err := vm.ParseVersion(to)
	if err != nil {
		return Incompatible, err
	}
	
	// Same version
	if v1.Major == v2.Major && v1.Minor == v2.Minor && v1.Patch == v2.Patch {
		return FullyCompatible, nil
	}
	
	// Different major versions are incompatible
	if v1.Major != v2.Major {
		return Incompatible, nil
	}
	
	// Same major, newer minor/patch is backward compatible
	if v1.Major == v2.Major {
		if v2.Minor > v1.Minor || (v2.Minor == v1.Minor && v2.Patch > v1.Patch) {
			return BackwardCompatible, nil
		}
		if v2.Minor < v1.Minor || (v2.Minor == v1.Minor && v2.Patch < v1.Patch) {
			return ForwardCompatible, nil
		}
	}
	
	return Incompatible, nil
}

// GetMigrationPath provides migration guidance
// माइग्रेशन गाइडेंस प्रदान करता है
func (vm *RazorpayVersionManager) GetMigrationPath(from, to string) (*MigrationGuide, error) {
	fromMeta, exists := vm.versions[from]
	if !exists {
		return nil, fmt.Errorf("source version %s not found", from)
	}
	
	toMeta, exists := vm.versions[to]
	if !exists {
		return nil, fmt.Errorf("target version %s not found", to)
	}
	
	migration := MigrationGuide{
		FromVersion:   from,
		ToVersion:     to,
		CodeExamples:  make(map[string]string),
	}
	
	// Check if auto migration is possible
	compatibility, _ := vm.GetCompatibilityLevel(from, to)
	migration.AutoMigration = compatibility == BackwardCompatible
	
	// Collect all changes between versions
	var steps []string
	
	// Add version-specific migration steps
	if toMeta.Migration.FromVersion == from {
		steps = append(steps, toMeta.Migration.Steps...)
	} else {
		// Multi-step migration through intermediate versions
		steps = append(steps, fmt.Sprintf("Multi-step migration required from %s to %s", from, to))
	}
	
	// Add breaking change warnings
	for _, change := range toMeta.Changes {
		if change.Type == "breaking" {
			steps = append(steps, fmt.Sprintf("⚠️  Breaking change: %s", change.Description))
		}
	}
	
	migration.Steps = steps
	
	// Add code examples
	migration.CodeExamples["curl"] = vm.generateCurlExample(to)
	migration.CodeExamples["javascript"] = vm.generateJSExample(to)
	
	return &migration, nil
}

// generateCurlExample generates curl example for version
func (vm *RazorpayVersionManager) generateCurlExample(version string) string {
	return fmt.Sprintf(`curl -X POST https://api.razorpay.com/v%s/payments \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "X-API-Version: %s" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 50000,
    "currency": "INR",
    "method": "upi",
    "upi": {
      "vpa": "user@paytm"
    }
  }'`, strings.Split(version, ".")[0], version)
}

// generateJSExample generates JavaScript example for version
func (vm *RazorpayVersionManager) generateJSExample(version string) string {
	return fmt.Sprintf(`const razorpay = require('razorpay');

const instance = new razorpay({
  key_id: 'YOUR_KEY_ID',
  key_secret: 'YOUR_SECRET',
  api_version: '%s'
});

const payment = await instance.payments.create({
  amount: 50000, // Amount in paise (₹500)
  currency: 'INR',
  method: 'upi',
  upi: {
    vpa: 'user@paytm'
  }
});`, version)
}

// GetVersionStatus provides version status information
// वर्जन स्टेटस की जानकारी प्रदान करता है
func (vm *RazorpayVersionManager) GetVersionStatus(version string) (map[string]interface{}, error) {
	meta, exists := vm.versions[version]
	if !exists {
		return nil, fmt.Errorf("version %s not found", version)
	}
	
	status := map[string]interface{}{
		"version":     version,
		"status":      meta.Status,
		"description": meta.Description,
		"released":    meta.Version.ReleaseDate.Format("2006-01-02"),
	}
	
	if meta.Deprecated != nil {
		status["deprecated"] = true
		status["deprecated_at"] = meta.Deprecated.Format("2006-01-02")
	}
	
	if meta.SunsetDate != nil {
		status["sunset_at"] = meta.SunsetDate.Format("2006-01-02")
		status["days_until_sunset"] = int(time.Until(*meta.SunsetDate).Hours() / 24)
	}
	
	// Check breaking changes
	hasBreakingChanges := false
	for _, change := range meta.Changes {
		if change.Type == "breaking" {
			hasBreakingChanges = true
			break
		}
	}
	status["has_breaking_changes"] = hasBreakingChanges
	
	return status, nil
}

// ListVersions returns all available versions
// सभी उपलब्ध वर्जन लौटाता है
func (vm *RazorpayVersionManager) ListVersions() []string {
	versions := make([]string, 0, len(vm.versions))
	for version := range vm.versions {
		versions = append(versions, version)
	}
	
	// Sort versions
	sort.Slice(versions, func(i, j int) bool {
		cmp, _ := vm.CompareVersions(versions[i], versions[j])
		return cmp < 0
	})
	
	return versions
}

// ValidateVersionConstraint checks if version satisfies constraint
// वर्जन constraint को satisfy करता है या नहीं चेक करता है
func (vm *RazorpayVersionManager) ValidateVersionConstraint(version, constraint string) (bool, error) {
	// Simple constraint parsing (>=, >, <=, <, =)
	operators := []string{">=", "<=", ">", "<", "="}
	
	var operator, constraintVersion string
	for _, op := range operators {
		if strings.HasPrefix(constraint, op) {
			operator = op
			constraintVersion = strings.TrimSpace(constraint[len(op):])
			break
		}
	}
	
	if operator == "" {
		return false, fmt.Errorf("invalid constraint format: %s", constraint)
	}
	
	cmp, err := vm.CompareVersions(version, constraintVersion)
	if err != nil {
		return false, err
	}
	
	switch operator {
	case ">=":
		return cmp >= 0, nil
	case "<=":
		return cmp <= 0, nil
	case ">":
		return cmp > 0, nil
	case "<":
		return cmp < 0, nil
	case "=":
		return cmp == 0, nil
	}
	
	return false, fmt.Errorf("unknown operator: %s", operator)
}

// Main demonstration function
func main() {
	fmt.Println("💎 Razorpay Semantic Versioning Manager Demo")
	fmt.Println("============================================")
	
	vm := NewRazorpayVersionManager()
	
	// List all versions
	fmt.Println("\n📋 Available API Versions:")
	versions := vm.ListVersions()
	for _, version := range versions {
		status, _ := vm.GetVersionStatus(version)
		statusEmoji := "✅"
		if status["status"] == "deprecated" {
			statusEmoji = "⚠️"
		} else if status["status"] == "beta" {
			statusEmoji = "🧪"
		}
		fmt.Printf("  %s %s - %s\n", statusEmoji, version, status["description"])
	}
	
	// Version comparison
	fmt.Println("\n🔄 Version Comparison:")
	comparisons := [][2]string{
		{"1.0.0", "2.0.0"},
		{"2.0.0", "2.1.0"},
		{"2.1.0", "3.0.0-beta"},
	}
	
	for _, pair := range comparisons {
		cmp, _ := vm.CompareVersions(pair[0], pair[1])
		var relation string
		switch {
		case cmp < 0:
			relation = "older than"
		case cmp > 0:
			relation = "newer than"
		default:
			relation = "same as"
		}
		fmt.Printf("  %s is %s %s\n", pair[0], relation, pair[1])
	}
	
	// Compatibility checking
	fmt.Println("\n🔗 Compatibility Analysis:")
	compatibility, _ := vm.GetCompatibilityLevel("2.0.0", "2.1.0")
	fmt.Printf("  2.0.0 → 2.1.0: %d (Backward Compatible)\n", compatibility)
	
	compatibility, _ = vm.GetCompatibilityLevel("1.0.0", "2.0.0")
	fmt.Printf("  1.0.0 → 2.0.0: %d (Incompatible)\n", compatibility)
	
	// Migration guidance
	fmt.Println("\n🚀 Migration Guidance:")
	migration, err := vm.GetMigrationPath("1.0.0", "2.1.0")
	if err != nil {
		log.Printf("Migration error: %v", err)
	} else {
		fmt.Printf("  From: %s → To: %s\n", migration.FromVersion, migration.ToVersion)
		fmt.Printf("  Auto Migration: %t\n", migration.AutoMigration)
		fmt.Println("  Steps:")
		for i, step := range migration.Steps {
			fmt.Printf("    %d. %s\n", i+1, step)
		}
		
		fmt.Println("\n  Code Example (JavaScript):")
		fmt.Println(migration.CodeExamples["javascript"])
	}
	
	// Version constraint validation
	fmt.Println("\n✅ Constraint Validation:")
	constraints := []string{">=2.0.0", "<3.0.0", "=2.1.0"}
	testVersion := "2.1.0"
	
	for _, constraint := range constraints {
		valid, _ := vm.ValidateVersionConstraint(testVersion, constraint)
		status := "❌"
		if valid {
			status = "✅"
		}
		fmt.Printf("  %s %s %s: %s\n", testVersion, constraint, constraint, status)
	}
	
	// Version status details
	fmt.Println("\n📊 Version Status Details:")
	for _, version := range []string{"1.0.0", "2.1.0", "3.0.0-beta"} {
		status, _ := vm.GetVersionStatus(version)
		statusJSON, _ := json.MarshalIndent(status, "  ", "  ")
		fmt.Printf("  %s:\n%s\n", version, statusJSON)
	}
}