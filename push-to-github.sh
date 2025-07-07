#!/bin/bash

# Git Push Script for DStudio Repository
# This script will help you push the code to GitHub

echo "Setting up Git repository for DStudio..."

# Initialize git if not already initialized
if [ ! -d ".git" ]; then
    git init
    echo "Git repository initialized."
fi

# Add remote if not already added
if ! git remote | grep -q "origin"; then
    git remote add origin https://github.com/deepaucksharma/DStudio.git
    echo "Remote origin added."
fi

# Add all files
git add .
echo "All files added to staging."

# Commit with a message
echo "Enter commit message (or press Enter for default):"
read commit_message

if [ -z "$commit_message" ]; then
    commit_message="System Design Implementation Guide - Complete architecture with code examples"
fi

git commit -m "$commit_message"

# Force push to overwrite existing content
echo "Warning: This will overwrite all existing content in the repository!"
echo "Are you sure you want to continue? (yes/no)"
read confirmation

if [ "$confirmation" = "yes" ]; then
    git push -f origin main
    echo "Code pushed successfully!"
else
    echo "Push cancelled."
fi
