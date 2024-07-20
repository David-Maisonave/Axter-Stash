# Importing config dictionary
config = {
    # Define wrapper styles for different parts of the filename.
    # Use '[]' for square brackets, '{}' for curly brackets, '()' for parentheses, or an empty string for None.
    "wrapper_styles": {
        "studio": '[]',        # Modify these values to change how each part of the filename is wrapped.
        "title": '',         # Use '[]' for square brackets, '{}' for curly brackets, '()' for parentheses, or an empty string for None.
        "performers": '[]',    # Modify these values to change how each part of the filename is wrapped.
        "date": '[]',          # Use '[]' for square brackets, '{}' for curly brackets, '()' for parentheses, or an empty string for None.
        "height": '[]',        # Modify these values to change how each part of the filename is wrapped.
        "video_codec": '[]',   # Use '[]' for square brackets, '{}' for curly brackets, '()' for parentheses, or an empty string for None.
        "frame_rate": '[]',    # Modify these values to change how each part of the filename is wrapped.
        "tag": '[]'            # Modify these values to change how each tag part of the filename is wrapped.
    },
    # Define the separator to use between different parts of the filename.
    # Use '-' for hyphen, '_' for underscore, or ' ' for space.
    "separator": '-',  
    # Define the order of keys in the filename.
    # Use a list to specify the order of keys.
    # Valid keys are 'studio', 'title', 'performers', 'date', 'height', 'video_codec', 'frame_rate', and 'tags'.
    "key_order": [
        "studio",
        "title",
        "performers",
        "date",
        "height",
        "video_codec",
        "frame_rate",
        "tags"
    ],
    # Define keys to exclude from the formed filename
    # Specify keys to exclude from the filename formation process. (ie. "exclude_keys": ["studio", "date"],)
    "exclude_keys": ["studio", "performers", "date", "height", "video_codec", "frame_rate"],
    # Define whether files should be moved when renaming
    "move_files": False,
    # Define whether files should be renamed when moved
    "rename_files": True,
    # Define whether the script should run in dry run mode
    "dry_run": False,
    # Define whether the original file name should be used if title is empty
    "if_notitle_use_org_filename": True,
    # Define whether to add tag only if tag is not in file name
    "add_tag_if_not_in_name": True,
    # Define whether to rename all files missing tag names, or only the latest scene having an update
    # "rename_all_files": True,
    # Define the maximum number of tag keys to include in the filename (None for no limit)
    "max_tag_keys": 12,
    # Current Stash DB schema only allows maximum base file name length to be 255
    "max_filename_length": 255,
    "max_filefolder_length": 255, # For future useage
    "max_filebase_length": 255, # For future useage
    # GraphQL endpoint
    "graphql_endpoint": "http://localhost:9999/graphql", # Update with your endpoint
    # Define a whitelist of allowed tags or (None to allow all tags)
    "tag_whitelist": [],   #Example: "tag_whitelist": ["tag1", "tag2", "tag3"]
    # Define paths to exclude from modifications
    "exclude_paths": []     #Example: "exclude_paths": [r"/path/to/exclude1"]
}
