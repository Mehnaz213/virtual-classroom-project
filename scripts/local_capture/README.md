## Local Calibration Capture

Use `capture_cli.py` to record labeled webcam snippets for calibration or
in-house dataset creation.

```
python scripts/local_capture/capture_cli.py --out data/raw/local_calibration --frames 20
```

The script will prompt you with instructions (e.g., "look left", "look up"),
capture the requested number of frames for each label, and save them under
`data/raw/local_calibration/<SESSION_ID>`.

After collecting samples, run

```
python scripts/data_ingest.py ingest local_calibration
```

to convert them into the unified metadata format.


