#!/usr/bin/env python3
"""Creates the media files and database fixtures for Vesa's
Music Trainer."""

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "lib"))
from content_creator import main

if __name__ == "__main__":
    main()

