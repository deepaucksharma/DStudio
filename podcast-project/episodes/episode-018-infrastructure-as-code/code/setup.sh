#!/bin/bash
# Infrastructure as Code Setup Script
# यह script सभी tools और dependencies को install करती है
# Episode 18 के सभी examples run करने के लिए

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_command() {
    if command -v "$1" &> /dev/null; then
        log_success "$1 is already installed"
        return 0
    else
        log_warning "$1 is not installed"
        return 1
    fi
}

# Main setup function
main() {
    log_info "🚀 Starting Infrastructure as Code setup for Episode 18..."
    log_info "Setting up tools for Flipkart-style infrastructure automation"
    
    # Check if running on supported OS
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS="linux"
        log_info "Detected Linux OS"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
        log_info "Detected macOS"
    else
        log_error "Unsupported OS: $OSTYPE"
        exit 1
    fi
    
    # Update package manager
    log_info "Updating package manager..."
    if [[ "$OS" == "linux" ]]; then
        if command -v apt-get &> /dev/null; then
            sudo apt-get update
        elif command -v yum &> /dev/null; then
            sudo yum update -y
        fi
    elif [[ "$OS" == "macos" ]]; then
        if ! command -v brew &> /dev/null; then
            log_info "Installing Homebrew..."
            /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        fi
        brew update
    fi
    
    # Install essential tools
    install_essential_tools
    
    # Install cloud tools
    install_cloud_tools
    
    # Install IaC tools
    install_iac_tools
    
    # Install development tools
    install_development_tools
    
    # Setup Python environment
    setup_python_environment
    
    # Configure tools
    configure_tools
    
    # Verify installation
    verify_installation
    
    log_success "🎉 Setup completed successfully!"
    log_info "You can now run the Infrastructure as Code examples"
    print_next_steps
}

install_essential_tools() {
    log_info "📦 Installing essential tools..."
    
    # Git
    if ! check_command git; then
        if [[ "$OS" == "linux" ]]; then
            sudo apt-get install -y git || sudo yum install -y git
        elif [[ "$OS" == "macos" ]]; then
            brew install git
        fi
    fi
    
    # Curl
    if ! check_command curl; then
        if [[ "$OS" == "linux" ]]; then
            sudo apt-get install -y curl || sudo yum install -y curl
        elif [[ "$OS" == "macos" ]]; then
            brew install curl
        fi
    fi
    
    # Wget
    if ! check_command wget; then
        if [[ "$OS" == "linux" ]]; then
            sudo apt-get install -y wget || sudo yum install -y wget
        elif [[ "$OS" == "macos" ]]; then
            brew install wget
        fi
    fi
    
    # Unzip
    if ! check_command unzip; then
        if [[ "$OS" == "linux" ]]; then
            sudo apt-get install -y unzip || sudo yum install -y unzip
        elif [[ "$OS" == "macos" ]]; then
            brew install unzip
        fi
    fi
    
    # jq (JSON processor)
    if ! check_command jq; then
        if [[ "$OS" == "linux" ]]; then
            sudo apt-get install -y jq || sudo yum install -y jq
        elif [[ "$OS" == "macos" ]]; then
            brew install jq
        fi
    fi
}

install_cloud_tools() {
    log_info "☁️ Installing cloud tools..."
    
    # AWS CLI v2
    if ! check_command aws; then
        log_info "Installing AWS CLI v2..."
        if [[ "$OS" == "linux" ]]; then
            curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
            unzip awscliv2.zip
            sudo ./aws/install
            rm -rf awscliv2.zip aws/
        elif [[ "$OS" == "macos" ]]; then
            curl "https://awscli.amazonaws.com/AWSCLIV2.pkg" -o "AWSCLIV2.pkg"
            sudo installer -pkg AWSCLIV2.pkg -target /
            rm AWSCLIV2.pkg
        fi
    fi
    
    # Azure CLI
    if ! check_command az; then
        log_info "Installing Azure CLI..."
        if [[ "$OS" == "linux" ]]; then
            curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
        elif [[ "$OS" == "macos" ]]; then
            brew install azure-cli
        fi
    fi
    
    # Google Cloud SDK
    if ! check_command gcloud; then
        log_info "Installing Google Cloud SDK..."
        if [[ "$OS" == "linux" ]]; then
            echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | sudo tee -a /etc/apt/sources.list.d/google-cloud-sdk.list
            curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key --keyring /usr/share/keyrings/cloud.google.gpg add -
            sudo apt-get update && sudo apt-get install -y google-cloud-cli
        elif [[ "$OS" == "macos" ]]; then
            brew install --cask google-cloud-sdk
        fi
    fi
}

install_iac_tools() {
    log_info "🏗️ Installing Infrastructure as Code tools..."
    
    # Terraform
    if ! check_command terraform; then
        log_info "Installing Terraform..."
        TERRAFORM_VERSION="1.6.6"
        if [[ "$OS" == "linux" ]]; then
            wget -O- https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg
            echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list
            sudo apt update && sudo apt install -y terraform
        elif [[ "$OS" == "macos" ]]; then
            brew tap hashicorp/tap
            brew install hashicorp/tap/terraform
        fi
    fi
    
    # Ansible
    if ! check_command ansible; then
        log_info "Installing Ansible..."
        if [[ "$OS" == "linux" ]]; then
            sudo apt-get install -y software-properties-common
            sudo add-apt-repository --yes --update ppa:ansible/ansible
            sudo apt-get install -y ansible
        elif [[ "$OS" == "macos" ]]; then
            brew install ansible
        fi
    fi
    
    # Terragrunt
    if ! check_command terragrunt; then
        log_info "Installing Terragrunt..."
        TERRAGRUNT_VERSION="v0.54.8"
        if [[ "$OS" == "linux" ]]; then
            wget -O terragrunt "https://github.com/gruntwork-io/terragrunt/releases/download/${TERRAGRUNT_VERSION}/terragrunt_linux_amd64"
        elif [[ "$OS" == "macos" ]]; then
            wget -O terragrunt "https://github.com/gruntwork-io/terragrunt/releases/download/${TERRAGRUNT_VERSION}/terragrunt_darwin_amd64"
        fi
        chmod +x terragrunt
        sudo mv terragrunt /usr/local/bin/
    fi
    
    # Pulumi
    if ! check_command pulumi; then
        log_info "Installing Pulumi..."
        curl -fsSL https://get.pulumi.com | sh
        export PATH=$PATH:$HOME/.pulumi/bin
    fi
}

install_development_tools() {
    log_info "🛠️ Installing development tools..."
    
    # Python 3
    if ! check_command python3; then
        if [[ "$OS" == "linux" ]]; then
            sudo apt-get install -y python3 python3-pip python3-venv || sudo yum install -y python3 python3-pip
        elif [[ "$OS" == "macos" ]]; then
            brew install python3
        fi
    fi
    
    # Node.js
    if ! check_command node; then
        log_info "Installing Node.js..."
        if [[ "$OS" == "linux" ]]; then
            curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
            sudo apt-get install -y nodejs
        elif [[ "$OS" == "macos" ]]; then
            brew install node
        fi
    fi
    
    # Go
    if ! check_command go; then
        log_info "Installing Go..."
        GO_VERSION="1.21.5"
        if [[ "$OS" == "linux" ]]; then
            wget "https://golang.org/dl/go${GO_VERSION}.linux-amd64.tar.gz"
            sudo tar -C /usr/local -xzf "go${GO_VERSION}.linux-amd64.tar.gz"
            rm "go${GO_VERSION}.linux-amd64.tar.gz"
        elif [[ "$OS" == "macos" ]]; then
            brew install go
        fi
        
        # Add Go to PATH
        if ! grep -q "/usr/local/go/bin" ~/.bashrc 2>/dev/null; then
            echo 'export PATH=$PATH:/usr/local/go/bin' >> ~/.bashrc
            echo 'export GOPATH=$HOME/go' >> ~/.bashrc
            echo 'export PATH=$PATH:$GOPATH/bin' >> ~/.bashrc
        fi
    fi
    
    # Docker
    if ! check_command docker; then
        log_info "Installing Docker..."
        if [[ "$OS" == "linux" ]]; then
            curl -fsSL https://get.docker.com -o get-docker.sh
            sudo sh get-docker.sh
            sudo usermod -aG docker $USER
            rm get-docker.sh
        elif [[ "$OS" == "macos" ]]; then
            brew install --cask docker
        fi
    fi
    
    # kubectl
    if ! check_command kubectl; then
        log_info "Installing kubectl..."
        if [[ "$OS" == "linux" ]]; then
            curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
        elif [[ "$OS" == "macos" ]]; then
            curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/darwin/amd64/kubectl"
        fi
        chmod +x kubectl
        sudo mv kubectl /usr/local/bin/
    fi
}

setup_python_environment() {
    log_info "🐍 Setting up Python environment..."
    
    # Create virtual environment
    if [[ ! -d "venv" ]]; then
        log_info "Creating Python virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install Python dependencies
    if [[ -f "requirements.txt" ]]; then
        log_info "Installing Python dependencies..."
        pip install -r requirements.txt
    else
        log_warning "requirements.txt not found, installing basic dependencies..."
        pip install boto3 ansible pytest requests pandas matplotlib
    fi
    
    log_success "Python environment setup completed"
}

configure_tools() {
    log_info "⚙️ Configuring tools..."
    
    # Configure Git (if not already configured)
    if [[ -z "$(git config --global user.name 2>/dev/null)" ]]; then
        log_info "Configuring Git..."
        echo "Please enter your Git username:"
        read -r git_username
        echo "Please enter your Git email:"
        read -r git_email
        git config --global user.name "$git_username"
        git config --global user.email "$git_email"
    fi
    
    # Configure Terraform
    log_info "Configuring Terraform..."
    if [[ ! -d ~/.terraform.d ]]; then
        mkdir -p ~/.terraform.d
    fi
    
    # Create Terraform configuration for caching
    cat > ~/.terraform.d/terraformrc << EOF
plugin_cache_dir = "$HOME/.terraform.d/plugin-cache"
disable_checkpoint = true
EOF
    
    mkdir -p ~/.terraform.d/plugin-cache
    
    # Configure Ansible
    log_info "Configuring Ansible..."
    if [[ ! -f ~/.ansible.cfg ]]; then
        cat > ~/.ansible.cfg << EOF
[defaults]
host_key_checking = False
timeout = 30
gathering = smart
fact_caching = memory
stdout_callback = yaml
EOF
    fi
    
    log_success "Tools configuration completed"
}

verify_installation() {
    log_info "🔍 Verifying installation..."
    
    local tools=(
        "git"
        "curl"
        "aws"
        "terraform"
        "ansible"
        "python3"
        "node"
        "go"
        "docker"
        "kubectl"
        "jq"
    )
    
    local failed_tools=()
    
    for tool in "${tools[@]}"; do
        if check_command "$tool"; then
            continue
        else
            failed_tools+=("$tool")
        fi
    done
    
    if [[ ${#failed_tools[@]} -eq 0 ]]; then
        log_success "All tools installed successfully!"
    else
        log_error "The following tools failed to install:"
        printf ' - %s\n' "${failed_tools[@]}"
        log_warning "Please install these tools manually"
    fi
    
    # Check versions
    log_info "Tool versions:"
    echo "Terraform: $(terraform --version | head -n1)"
    echo "Ansible: $(ansible --version | head -n1)"
    echo "AWS CLI: $(aws --version)"
    echo "Python: $(python3 --version)"
    echo "Node.js: $(node --version)"
    echo "Go: $(go version)"
    echo "Docker: $(docker --version)"
    echo "kubectl: $(kubectl version --client --short 2>/dev/null)"
}

print_next_steps() {
    cat << EOF

🎯 Next Steps:

1. Configure AWS credentials:
   aws configure
   
2. Configure Azure credentials (if using Azure):
   az login
   
3. Test Terraform:
   cd terraform/
   terraform init
   terraform plan
   
4. Test Ansible:
   ansible --version
   ansible localhost -m ping
   
5. Run infrastructure tests:
   cd testing/
   go test -v
   
6. Run cost optimization:
   python cost-optimization/01_cost_optimization_setup.py

📚 Documentation:
   - Main README: ./README.md
   - Code Examples Summary: ./CODE_EXAMPLES_SUMMARY.md
   - Each directory has its own README with specific instructions

💡 Tips:
   - Use 'source venv/bin/activate' to activate Python environment
   - All examples are designed for Mumbai region (ap-south-1)
   - Start with development environment before production
   - Review cost implications before deploying to production

🆘 Need Help?
   - Check troubleshooting section in README.md
   - Review logs in /tmp/setup.log if errors occur
   - Ensure you have proper AWS/Azure permissions

Happy Infrastructure Coding! 🚀

EOF
}

# Error handling
trap 'log_error "Setup failed at line $LINENO. Check the logs for details."' ERR

# Create log file
exec 1> >(tee -a /tmp/setup.log)
exec 2> >(tee -a /tmp/setup.log >&2)

# Run main function
main "$@"