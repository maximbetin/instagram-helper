#!/bin/bash

# Instagram Helper - WSL2 Development Environment Setup Script
# This script sets up a complete development environment for Instagram Helper

set -e  # Exit on any error

echo "🚀 Setting up Instagram Helper development environment for WSL2..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Python 3.12+ is available
check_python() {
    print_status "Checking Python version..."
    
    if command -v python3.12 &> /dev/null; then
        PYTHON_CMD="python3.12"
        print_success "Found Python 3.12"
    elif command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version 2>&1 | grep -oP '\d+\.\d+' | head -1)
        if [[ $(echo "$PYTHON_VERSION >= 3.12" | bc -l 2>/dev/null) -eq 1 ]]; then
            PYTHON_CMD="python3"
            print_success "Found Python $PYTHON_VERSION"
        else
            print_error "Python 3.12+ is required. Found version $PYTHON_VERSION"
            exit 1
        fi
    else
        print_error "Python 3.12+ is not installed"
        exit 1
    fi
}

# Check if Node.js is available
check_node() {
    print_status "Checking Node.js..."
    
    if command -v node &> /dev/null; then
        NODE_VERSION=$(node --version)
        print_success "Found Node.js $NODE_VERSION"
    else
        print_warning "Node.js not found. Installing via apt..."
        sudo apt update
        sudo apt install -y nodejs npm
        print_success "Node.js installed"
    fi
}

# Create and activate virtual environment
setup_venv() {
    print_status "Setting up Python virtual environment..."
    
    if [ ! -d "venv" ]; then
        $PYTHON_CMD -m venv venv
        print_success "Virtual environment created"
    else
        print_status "Virtual environment already exists"
    fi
    
    # Source the virtual environment
    source venv/bin/activate
    print_success "Virtual environment activated"
}

# Install Python dependencies
install_python_deps() {
    print_status "Installing Python dependencies..."
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install the package in development mode
    pip install -e ".[dev]"
    
    print_success "Python dependencies installed"
}

# Install Node.js dependencies
install_node_deps() {
    print_status "Installing Node.js dependencies..."
    
    npm install
    
    print_success "Node.js dependencies installed"
}

# Install Playwright browsers
install_browsers() {
    print_status "Installing Playwright browsers..."
    
    playwright install --with-deps
    
    print_success "Playwright browsers installed"
}

# Run initial quality checks
run_quality_checks() {
    print_status "Running initial quality checks..."
    
    echo ""
    echo "🔍 Running Ruff linting..."
    ruff check . || print_warning "Some linting issues found (this is normal for initial setup)"
    
    echo ""
    echo "🔍 Running MyPy type checking..."
    mypy . || print_warning "Some type checking issues found (this is normal for initial setup)"
    
    echo ""
    echo "🔍 Running Prettier check on README.md..."
    npm run format:check || print_warning "README.md formatting issues found"
    
    echo ""
    echo "🧪 Running tests..."
    pytest tests/ -v || print_warning "Some tests may have failed (this is normal for initial setup)"
    
    print_success "Quality checks completed"
}

# Show next steps
show_next_steps() {
    echo ""
    echo "🎉 Development environment setup complete!"
    echo ""
    echo "Next steps:"
    echo "1. Activate the virtual environment:"
    echo "   source venv/bin/activate"
    echo ""
    echo "2. Available development commands:"
    echo "   make help           # Show all available commands"
    echo "   make lint           # Run linting"
    echo "   make format         # Format code"
    echo "   make test           # Run tests"
    echo "   make check-all      # Run all quality checks"
    echo ""
    echo "3. To format README.md:"
    echo "   make format-readme"
    echo ""
    echo "4. To run the application:"
    echo "   make run"
    echo ""
    echo "Happy coding! 🚀"
}

# Main setup function
main() {
    echo ""
    echo "=========================================="
    echo "Instagram Helper - WSL2 Dev Setup"
    echo "=========================================="
    echo ""
    
    check_python
    check_node
    setup_venv
    install_python_deps
    install_node_deps
    install_browsers
    run_quality_checks
    show_next_steps
}

# Run main function
main "$@"
