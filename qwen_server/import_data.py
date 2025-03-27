import json
import os
import shutil
from pathlib import Path
import datetime
from qwen_agent.utils.utils import get_basename_from_url, hash_sha256, save_text_to_file
from qwen_server.schema import GlobalConfig
from qwen_server.utils import (
    read_meta_data_by_condition,
    save_browsing_meta_data,
    save_history,
    rm_browsing_meta_data,
)
from qwen_server.database_server import cache_page, update_pop_url

server_config_path = Path(__file__).resolve().parent / "server_config.json"
with open(server_config_path, "r") as f:
    server_config = json.load(f)
    server_config = GlobalConfig(**server_config)

# Clean up and create workspace directories
if os.path.exists("workspace"):
    shutil.rmtree("workspace")
os.makedirs(server_config.path.work_space_root)
os.makedirs(server_config.path.download_root)
os.makedirs(server_config.path.code_interpreter_ws)

# Define the data to import
data = {
    "url": "https://system.reins.jp/login/main/KG/GKG001200",
    "content": "- Input the following information to login from login page \n"
    "Username: 134550110127\n"
    "Password: fine77\n"
    "- Select on the check box 所属機構の規程及びガイドラインを遵守します\n"
    "- Click on ログイン button\n",
}

# Get the new local URL first
new_url = os.path.join(
    server_config.path.download_root,
    hash_sha256(data["url"]),
    get_basename_from_url(data["url"]),
)
print(f"New URL will be: {new_url}")

# Create directory and save content
os.makedirs(os.path.dirname(new_url), exist_ok=True)
save_text_to_file(new_url, data["content"])

# Save metadata with initial [CACHING] title
save_browsing_meta_data(
    new_url,
    "[CACHING]",
    os.path.join(server_config.path.work_space_root, "meta_data.jsonl"),
)

# Clear history if exists
history_dir = os.path.join(server_config.path.work_space_root, "history")
save_history(None, new_url, history_dir)

# Update popup URL
update_pop_url(new_url)

# Verify the file exists
assert os.path.exists(new_url), f"File not found at {new_url}"

# Verify metadata
meta_file = os.path.join(server_config.path.work_space_root, "meta_data.jsonl")
assert os.path.exists(meta_file), f"Metadata file not found at {meta_file}"

# Read and verify metadata
res = read_meta_data_by_condition(meta_file, url=new_url)
assert res != "", f"No metadata found for URL {new_url}"
assert isinstance(res, dict), f"Metadata is not a dictionary: {type(res)}"
assert res["url"] == new_url, f"URL mismatch: expected {new_url}, got {res['url']}"

# Update popup URL
cache_file_popup_url = os.path.join(
    server_config.path.work_space_root, "popup_url.jsonl"
)
assert os.path.exists(
    cache_file_popup_url
), f"Popup URL file not found at {cache_file_popup_url}"

print("\nData import successful!")
