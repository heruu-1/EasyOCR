#!/bin/bash
# Script untuk test dependencies sebelum Docker build

echo "🔍 Testing package availability..."

# Test base image
echo "Testing base image: python:3.10-slim-bullseye"
docker run --rm python:3.10-slim-bullseye apt-get update > /dev/null 2>&1

if [ $? -eq 0 ]; then
    echo "✅ Base image accessible"
else
    echo "❌ Base image issue"
    exit 1
fi

# Test specific packages
packages=(
    "tesseract-ocr"
    "tesseract-ocr-eng" 
    "tesseract-ocr-ind"
    "poppler-utils"
    "libglib2.0-0"
    "libgcc-s1"
    "libstdc++6"
    "wget"
)

echo "Testing package availability..."
for package in "${packages[@]}"; do
    echo -n "Testing $package... "
    docker run --rm python:3.10-slim-bullseye sh -c "apt-get update > /dev/null 2>&1 && apt-cache show $package > /dev/null 2>&1"
    if [ $? -eq 0 ]; then
        echo "✅"
    else
        echo "❌ Package $package not found"
    fi
done

echo "🎉 Dependency check complete"
