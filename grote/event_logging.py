from __future__ import annotations

import csv
import json
import uuid
from pathlib import Path
from typing import Any

import filelock
import huggingface_hub
from gradio import HuggingFaceDatasetSaver, utils


class HuggingFaceDatasetEventSaver(HuggingFaceDatasetSaver):
    """Override of HuggingFaceDatasetSaver to handle saving logged events in a state object."""

    def setup(self, logging_dir: str, features: dict[str, dict[str, str]]):
        """
        Params:
            flagging_dir (str): local directory where the dataset is cloned, updated, and pushed from.
        """
        self.features = features

        # Setup dataset on the Hub
        self.dataset_id = huggingface_hub.create_repo(
            repo_id=self.dataset_id,
            token=self.hf_token,
            private=self.dataset_private,
            repo_type="dataset",
            exist_ok=True,
        ).repo_id
        path_glob = "**/*.jsonl" if self.separate_dirs else "data.csv"
        huggingface_hub.metadata_update(
            repo_id=self.dataset_id,
            repo_type="dataset",
            metadata={
                "configs": [
                    {
                        "config_name": "default",
                        "data_files": [{"split": "train", "path": path_glob}],
                    }
                ]
            },
            overwrite=True,
            token=self.hf_token,
        )

        # Setup flagging dir
        self.dataset_dir = Path(logging_dir).absolute() / self.dataset_id.split("/")[-1]
        self.dataset_dir.mkdir(parents=True, exist_ok=True)
        self.infos_file = self.dataset_dir / self.info_filename

        # Download remote files to local
        remote_files = [self.info_filename]
        if not self.separate_dirs:
            # No separate dirs => means all data is in the same CSV file => download it to get its current content
            remote_files.append("data.csv")

        for filename in remote_files:
            try:
                huggingface_hub.hf_hub_download(
                    repo_id=self.dataset_id,
                    repo_type="dataset",
                    filename=filename,
                    local_dir=self.dataset_dir,
                    token=self.hf_token,
                )
            except huggingface_hub.utils.EntryNotFoundError:
                pass

    def save(self, data: list[dict[str, Any]]) -> int:
        if self.separate_dirs:
            # JSONL files to support dataset preview on the Hub
            unique_id = str(uuid.uuid4())
            data_dir = self.dataset_dir / unique_id
            data_file = data_dir / "metadata.jsonl"
            path_in_repo = unique_id  # upload in sub folder (safer for concurrency)
        else:
            # Unique CSV file
            data_dir = self.dataset_dir
            data_file = data_dir / "data.csv"
            path_in_repo = None  # upload at root level

        return self._save_in_dir(
            data_file=data_file,
            data_dir=data_dir,
            path_in_repo=path_in_repo,
            data=data,
        )

    def _save_in_dir(
        self,
        data_file: Path,
        data_dir: Path,
        path_in_repo: str | None,
        data: list[Any],
    ) -> int:
        # Deserialize components (write images/audio to files)
        rows = self._format_data(data_dir, data)

        # Write generic info to dataset_infos.json + upload
        with filelock.FileLock(str(self.infos_file) + ".lock"):
            if not self.infos_file.exists():
                self.infos_file.write_text(json.dumps({"features": self.features}))

                huggingface_hub.upload_file(
                    repo_id=self.dataset_id,
                    repo_type="dataset",
                    token=self.hf_token,
                    path_in_repo=self.infos_file.name,
                    path_or_fileobj=self.infos_file,
                )

        headers = list(self.features.keys())

        if not self.separate_dirs:
            with filelock.FileLock(data_dir / ".lock"):
                sample_nb = self._save_as_csv(data_file, headers=headers, rows=rows)
                sample_name = str(sample_nb)
                huggingface_hub.upload_folder(
                    repo_id=self.dataset_id,
                    repo_type="dataset",
                    commit_message=f"Logged events up to #{sample_name}",
                    path_in_repo=path_in_repo,
                    ignore_patterns="*.lock",
                    folder_path=data_dir,
                    token=self.hf_token,
                )
        else:
            sample_name = self._save_as_jsonl(data_file, headers=headers, rows=rows)
            sample_nb = len([path for path in self.dataset_dir.iterdir() if path.is_dir()])
            huggingface_hub.upload_folder(
                repo_id=self.dataset_id,
                repo_type="dataset",
                commit_message=f"Logged events up to #{sample_name}",
                path_in_repo=path_in_repo,
                ignore_patterns="*.lock",
                folder_path=data_dir,
                token=self.hf_token,
            )

        return sample_nb

    def _format_data(self, data_dir: Path, data: list[dict[str, Any]]) -> tuple[dict[Any, Any], list[Any]]:
        """Standardize logged events for writing to disk."""
        rows = []
        for event in data:
            row = []
            for feature in self.features.keys():
                if feature in event:
                    row.append(event[feature])
                else:
                    row.append(None)
            rows.append(row)
        return rows

    @staticmethod
    def sanitize_list_for_csv(values: list[Any]) -> list[Any]:
        """
        Sanitizes a list of values (or a list of list of values) that is being written to a
        CSV file to prevent CSV injection attacks.
        """
        sanitized_values = []
        for value in values:
            if isinstance(value, list):
                sanitized_value = [utils.sanitize_value_for_csv(v) if v is not None else v for v in value]
                sanitized_values.append(sanitized_value)
            else:
                sanitized_value = utils.sanitize_value_for_csv(value) if value is not None else v
                sanitized_values.append(sanitized_value)
        return sanitized_values

    @classmethod
    def _save_as_csv(cls, data_file: Path, headers: list[str], rows: list[list[Any]]) -> int:
        """Save data as CSV and return the sample name (row number)."""
        is_new = not data_file.exists()

        with data_file.open("a", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)

            # Write CSV headers if new file
            if is_new:
                writer.writerow(utils.sanitize_list_for_csv(headers))

            # Write CSV row for flagged sample
            writer.writerows(cls.sanitize_list_for_csv(rows))

        with data_file.open(encoding="utf-8") as csvfile:
            return sum(1 for _ in csv.reader(csvfile)) - 1

    @staticmethod
    def _save_as_jsonl(data_file: Path, headers: list[str], rows: list[list[Any]]) -> str:
        """Save data as JSONL and return the sample name (uuid)."""
        Path.mkdir(data_file.parent, parents=True, exist_ok=True)
        with open(data_file, "w") as f:
            save_dic = {}
            for i, header in enumerate(headers):
                save_dic[header] = [row[i] for row in rows]
            json.dump(save_dic, f)
        return data_file.parent.name
