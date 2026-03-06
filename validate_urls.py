#!/usr/bin/env python3
"""
Radio URL Validator

This script validates radio stream URLs from a JSON file.
Valid URLs remain in the original file, invalid URLs are moved to old.json.

Usage:
    python validate_urls.py --input data/index.json
    python validate_urls.py --input data/active.json
"""

import json
import argparse
import urllib.request
import urllib.error
import ssl
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Tuple
import time


def create_ssl_context():
    """Create SSL context that allows us to check URLs with SSL issues."""
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    # Allow legacy renegotiation for old servers
    context.options |= ssl.OP_LEGACY_SERVER_CONNECT
    return context


def create_legacy_ssl_context():
    """Create a more permissive SSL context for very old servers."""
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    context.options |= ssl.OP_LEGACY_SERVER_CONNECT
    # Set minimum version to TLS 1.0 to support older servers
    context.minimum_version = ssl.TLSVersion.TLSv1
    return context


def check_url(url: str, timeout: int = 15) -> Tuple[bool, str]:
    """
    Check if a URL is valid and accessible.
    
    Args:
        url: The URL to check
        timeout: Request timeout in seconds
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not url or not isinstance(url, str):
        return False, "Empty or invalid URL"
    
    # Ensure URL starts with http
    if not url.startswith(('http://', 'https://')):
        return False, f"Invalid URL scheme: {url}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': '*/*',
        'Accept-Encoding': 'identity;q=1, *;q=0',
        'Accept-Language': 'en-US,en;q=0.9',
        'Range': 'bytes=0-1024',
    }
    
    try:
        req = urllib.request.Request(url, headers=headers, method='HEAD')
        context = create_ssl_context()
        
        with urllib.request.urlopen(req, timeout=timeout, context=context) as response:
            status_code = response.getcode()
            
            # 2xx and 3xx status codes are generally valid
            if 200 <= status_code < 400:
                return True, f"OK ({status_code})"
            else:
                return False, f"HTTP {status_code}"
                
    except ssl.SSLError as e:
        # Try with legacy SSL context for old servers
        error_str = str(e)
        if 'HANDSHAKE_FAILURE' in error_str or 'SSL' in error_str:
            try:
                req = urllib.request.Request(url, headers=headers, method='HEAD')
                legacy_context = create_legacy_ssl_context()
                with urllib.request.urlopen(req, timeout=timeout, context=legacy_context) as response:
                    status_code = response.getcode()
                    if 200 <= status_code < 400:
                        return True, f"OK ({status_code}) - legacy SSL"
                    else:
                        return False, f"HTTP {status_code}"
            except:
                pass
        return False, f"SSL/Certificate error: {error_str}"
                
    except urllib.error.HTTPError as e:
        # HTTP errors (404, 500, etc.)
        if e.code == 404:
            return False, f"HTTP 404 - Not Found"
        elif e.code == 403:
            return False, f"HTTP 403 - Forbidden"
        elif e.code == 500:
            return False, f"HTTP 500 - Server Error"
        elif e.code == 502:
            return False, f"HTTP 502 - Bad Gateway"
        elif e.code == 503:
            return False, f"HTTP 503 - Service Unavailable"
        else:
            return False, f"HTTP {e.code}"
            
    except urllib.error.URLError as e:
        # Connection errors, DNS failures, etc.
        error_str = str(e.reason)
        if 'Name or service not known' in error_str or 'getaddrinfo failed' in error_str:
            return False, "DNS resolution failed"
        elif 'Connection refused' in error_str:
            return False, "Connection refused"
        elif 'Connection timed out' in error_str or 'timed out' in error_str:
            return False, "Connection timeout"
        elif 'certificate' in error_str.lower():
            return False, f"SSL/Certificate error: {error_str}"
        elif 'No route to host' in error_str:
            return False, "No route to host"
        else:
            return False, f"URL Error: {error_str}"
            
    except TimeoutError:
        return False, "Request timeout"
    except Exception as e:
        return False, f"Error: {str(e)}"


def validate_station(station: Dict) -> Tuple[Dict, bool, str]:
    """
    Validate a single radio station's stream URL.
    
    Args:
        station: Dictionary containing station data with 'streamUrl' key
        
    Returns:
        Tuple of (station, is_valid, error_message)
    """
    stream_url = station.get('streamUrl', '')
    is_valid, message = check_url(stream_url)
    return station, is_valid, message


def validate_urls(input_file: str, invalid_file: str, max_workers: int = 10, dry_run: bool = False) -> None:
    """
    Validate all URLs in a JSON file and separate invalid ones.
    
    Args:
        input_file: Path to input JSON file containing radio stations
        invalid_file: Path to output JSON file for invalid stations
        max_workers: Number of concurrent threads for validation
        dry_run: If True, don't modify files, just show results
    """
    # Load the input file
    print(f"Loading stations from: {input_file}")
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            stations = json.load(f)
    except FileNotFoundError:
        print(f"Error: File '{input_file}' not found.")
        return
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in '{input_file}': {e}")
        return
    
    if not isinstance(stations, list):
        print(f"Error: Expected a list of stations in '{input_file}'")
        return
    
    total = len(stations)
    print(f"Total stations to validate: {total}")
    print(f"Using {max_workers} concurrent workers...")
    print("-" * 60)
    
    valid_stations = []
    invalid_stations = []
    
    # Validate URLs concurrently
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_station = {
            executor.submit(validate_station, station): station 
            for station in stations
        }
        
        completed = 0
        for future in as_completed(future_to_station):
            station, is_valid, message = future.result()
            completed += 1
            
            station_name = station.get('name', 'Unknown')
            stream_url = station.get('streamUrl', 'N/A')
            
            # Add validation info to station data
            station['_validation'] = {
                'valid': is_valid,
                'message': message,
                'checked_at': time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())
            }
            
            if is_valid:
                valid_stations.append(station)
                status = "✓ VALID"
            else:
                invalid_stations.append(station)
                status = "✗ INVALID"
            
            # Progress output
            print(f"[{completed}/{total}] {status}: {station_name}")
            print(f"    URL: {stream_url[:70]}{'...' if len(stream_url) > 70 else ''}")
            print(f"    Result: {message}")
            print()
    
    print("-" * 60)
    print(f"Validation complete!")
    print(f"  Valid stations:   {len(valid_stations)}")
    print(f"  Invalid stations: {len(invalid_stations)}")
    print()
    
    # Remove validation metadata from valid stations before saving
    for station in valid_stations:
        station.pop('_validation', None)
    
    # List invalid stations
    if invalid_stations:
        print("Invalid stations:")
        for station in invalid_stations:
            print(f"  - {station.get('name', 'Unknown')}: {station['_validation']['message']}")
        print()
    
    if dry_run:
        print("DRY RUN: No files were modified.")
        print(f"Would write {len(valid_stations)} stations to: {input_file}")
        print(f"Would write {len(invalid_stations)} stations to: {invalid_file}")
        return
    
    # Write valid stations back to original file
    with open(input_file, 'w', encoding='utf-8') as f:
        json.dump(valid_stations, f, indent=4, ensure_ascii=False)
    print(f"Updated {input_file} with {len(valid_stations)} valid stations")
    
    # Write invalid stations to separate file
    with open(invalid_file, 'w', encoding='utf-8') as f:
        json.dump(invalid_stations, f, indent=4, ensure_ascii=False)
    print(f"Saved {len(invalid_stations)} invalid stations to {invalid_file}")


def main():
    parser = argparse.ArgumentParser(
        description='Validate radio stream URLs and separate invalid ones.'
    )
    parser.add_argument(
        '--input', '-i',
        default='data/index.json',
        help='Input JSON file with radio stations (default: data/index.json)'
    )
    parser.add_argument(
        '--invalid', '-o',
        default='data/old.json',
        help='Output file for invalid stations (default: data/old.json)'
    )
    parser.add_argument(
        '--workers', '-w',
        type=int,
        default=10,
        help='Number of concurrent validation threads (default: 10)'
    )
    parser.add_argument(
        '--dry-run', '-d',
        action='store_true',
        help='Show results without modifying files'
    )
    
    args = parser.parse_args()
    
    validate_urls(
        input_file=args.input,
        invalid_file=args.invalid,
        max_workers=args.workers,
        dry_run=args.dry_run
    )


if __name__ == '__main__':
    main()
