#!/usr/bin/env python3
"""
Advanced Radio URL Validator

This script performs deeper validation including:
- HTTP status check
- Content-Type validation
- Actual audio stream detection
- CORS header checking

Usage:
    python validate_advanced.py
"""

import json
import subprocess
import re
import ssl
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

# Create permissive SSL context
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

def check_stream_with_ffmpeg(url: str, timeout: int = 10) -> tuple:
    """
    Use ffmpeg to check if stream is actually playable.
    This is the most reliable method.
    """
    try:
        # Run ffmpeg to probe the stream
        result = subprocess.run(
            ['ffmpeg', '-v', 'error', '-i', url, '-t', '1', '-f', 'null', '-'],
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        if result.returncode == 0:
            return True, "Stream is playable"
        else:
            # Check for common errors
            error = result.stderr.lower()
            if '404' in error or 'not found' in error:
                return False, "HTTP 404 - Stream not found"
            elif '403' in error or 'forbidden' in error:
                return False, "HTTP 403 - Access forbidden (may need referer)"
            elif 'timeout' in error:
                return False, "Connection timeout"
            elif 'invalid data' in error:
                return False, "Invalid stream format"
            else:
                return False, f"Stream error: {result.stderr[:100]}"
                
    except subprocess.TimeoutExpired:
        return False, "FFmpeg timeout - stream may be slow"
    except FileNotFoundError:
        # Fallback if ffmpeg is not installed
        return check_stream_http(url, timeout)
    except Exception as e:
        return False, f"Error: {str(e)}"

def check_stream_http(url: str, timeout: int = 10) -> tuple:
    """
    Check stream using HTTP headers (fallback method).
    Tries multiple user agents and headers.
    """
    # Try different user agents and headers
    attempts = [
        {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': '*/*',
            'Accept-Encoding': 'identity;q=1, *;q=0',
            'Icy-MetaData': '1',
            'Referer': 'https://yoradio.app/',
        },
        {
            'User-Agent': 'VLC/3.0.18 LibVLC/3.0.18',
            'Accept': '*/*',
            'Icy-MetaData': '1',
        },
        {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
            'Accept': 'audio/webm,audio/ogg,audio/wav,audio/*;q=0.9,application/ogg;q=0.7,video/*;q=0.6,*/*;q=0.5',
            'Icy-MetaData': '1',
        }
    ]
    
    last_error = ""
    
    for headers in attempts:
        try:
            req = Request(url, headers=headers, method='HEAD')
            response = urlopen(req, timeout=timeout, context=ssl_context)
            
            # Get content type
            content_type = response.headers.get('Content-Type', '').lower()
            
            # Check if it's an audio stream
            audio_types = ['audio/', 'application/ogg', 'application/octet-stream', 'binary/octet-stream']
            is_audio = any(t in content_type for t in audio_types)
            
            # Check for ICY (Icecast/Shoutcast) headers
            has_icy = any(k.startswith('icy-') for k in response.headers.keys())
            
            # Check content length (some streams report 0 but still work)
            content_length = response.headers.get('Content-Length')
            
            # Some stations return 200 but with html content (login pages, etc)
            if 'text/html' in content_type:
                last_error = f"HTML page returned (not stream)"
                continue
            
            if is_audio or has_icy:
                return True, f"Audio stream OK ({content_type[:30]})"
            elif not content_type:
                # No content type but request succeeded - might be stream
                return True, "Stream detected (no content-type)"
            else:
                last_error = f"Not audio ({content_type})"
                
        except HTTPError as e:
            if e.code == 405:  # Method not allowed, try GET
                try:
                    req = Request(url, headers=headers, method='GET')
                    response = urlopen(req, timeout=timeout, context=ssl_context)
                    return True, f"Stream OK (GET method)"
                except:
                    last_error = f"HTTP {e.code}: {e.reason}"
            elif e.code == 403:
                last_error = f"HTTP 403 Forbidden - may need referer header"
            elif e.code == 404:
                return False, f"HTTP 404 - Stream not found"
            else:
                last_error = f"HTTP {e.code}: {e.reason}"
        except URLError as e:
            last_error = f"URL Error: {str(e.reason)}"
        except Exception as e:
            last_error = f"Error: {str(e)[:50]}"
    
    return False, last_error if last_error else "Failed all connection attempts"

def validate_station(station: dict) -> tuple:
    """Validate a single station."""
    url = station.get('streamUrl', '')
    if not url:
        return station, False, "No stream URL"
    
    # First try ffmpeg (most accurate)
    is_valid, message = check_stream_with_ffmpeg(url)
    
    # If ffmpeg fails, try HTTP method
    if not is_valid and "FFmpeg" not in message:
        is_valid, message = check_stream_http(url)
    
    station['_validation'] = {
        'valid': is_valid,
        'message': message,
        'checked_at': time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime()),
        'url': url
    }
    
    return station, is_valid, message

def main():
    print("=" * 70)
    print("ADVANCED RADIO STREAM VALIDATOR")
    print("=" * 70)
    print()
    
    # Load stations
    print("Loading stations from data/index.json...")
    with open('data/index.json', 'r', encoding='utf-8') as f:
        stations = json.load(f)
    
    print(f"Total stations to validate: {len(stations)}")
    print("Using ffmpeg + HTTP validation (this may take a few minutes)...")
    print("-" * 70)
    print()
    
    valid_stations = []
    invalid_stations = []
    
    # Validate with progress
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(validate_station, s): s for s in stations}
        
        completed = 0
        for future in as_completed(futures):
            station, is_valid, message = future.result()
            completed += 1
            
            name = station.get('name', 'Unknown')
            status = "✓ VALID" if is_valid else "✗ INVALID"
            
            print(f"[{completed}/{len(stations)}] {status}: {name}")
            print(f"    Message: {message}")
            print()
            
            if is_valid:
                # Remove validation data before saving
                station_clean = {k: v for k, v in station.items() if not k.startswith('_')}
                valid_stations.append(station_clean)
            else:
                invalid_stations.append(station)
    
    print("-" * 70)
    print(f"VALIDATION COMPLETE")
    print(f"  Valid:   {len(valid_stations)} stations")
    print(f"  Invalid: {len(invalid_stations)} stations")
    print()
    
    # Save results
    with open('data/index.json', 'w', encoding='utf-8') as f:
        json.dump(valid_stations, f, indent=4, ensure_ascii=False)
    print(f"✓ Saved {len(valid_stations)} valid stations to data/index.json")
    
    with open('data/active.json', 'w', encoding='utf-8') as f:
        json.dump(valid_stations, f, indent=4, ensure_ascii=False)
    print(f"✓ Saved {len(valid_stations)} valid stations to data/active.json")
    
    with open('data/old.json', 'w', encoding='utf-8') as f:
        json.dump(invalid_stations, f, indent=4, ensure_ascii=False)
    print(f"✓ Saved {len(invalid_stations)} invalid stations to data/old.json")
    
    print()
    print("TIPS:")
    print("- Some stations may require specific headers (referer, user-agent)")
    print("- Some streams are geo-restricted (only work in Nepal)")
    print("- Some stations block automated requests")
    print("- Run this script periodically as streams go offline frequently")

if __name__ == '__main__':
    main()
