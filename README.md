# GroTE: Groningen Translation Environment 🐮

## Demo example

An online GroTE demo is available at [https://grote-app.hf.space](https://grote-app.hf.space). You can use `admin` as a login code, and upload one of the files in [assets/examples](assets/examples/en_it.txt) for the editing. The demo will log events to the repository [grote/grote-logs](https://huggingface.co/datasets/grote/grote-logs).

## Running GroTE locally

1. Install requirements: `pip install -r requirements.txt`.
2. Make sure you have a local `npm` installation available to run the front-end.
3. Edit the [GroTE config](grote/config.yaml) to set your custom `login_codes` and `event_logs_hf_dataset_id`. By default, you will be able to access the demo using the `admin` code, and logs will be written to a local `logs` directory, and synchronized with a private `grote-logs` dataset on your user profile in the Hugging Face Hub.
4. Run `grote` in your command line to start the server. You will need a Hugging Face token with `Write` permissions to log edits.
5. Visit http://127.0.0.1:7860 to access the demo.
6. Enter your login code and load an example document from [assets/examples](assets/examples/en_it.txt).
7. Press "📝 Start" to begin editing the document.

## Setting up a new GroTE instance on HF Spaces

1. Use the "Duplicate this space" option from the [original GroTE demo](https://huggingface.co/spaces/grote/app) to create a copy in your user/organization profile.
2. In Settings > Variables and secrets, change the default value of `EVENT_LOGS_HF_DATASET_ID`, `HF_TOKEN` and `LOGIN_CODES` to your desired values (see [GroTE config](grote/config.yaml) for more details).
3. Upon running the app and starting the editing, you should see the logs being written to the dataset having the id is specified in `EVENT_LOGS_HF_DATASET_ID`.

Use or modify the following code to create multiple copies of the app programmatically:

```python
from huggingface_hub import duplicate_space, SpaceHardware

NUM_TRANSLATORS = 5
USER_OR_ORG = "<your_username_or_organization>"
YOUR_HF_TOKEN = "hf_<your_token>"

names = [f"translator-{idx}" for idx in range(1, NUM_TRANSLATORS + 1)]

for name in names:
    duplicate_space(
        from_id="grote/app",
        to_id=f"{USER_OR_ORG}/grote-{name}",
        private=False,
        token=YOUR_HF_TOKEN,
        hardware=SpaceHardware.CPU_BASIC,
        secrets=[
            {
                "key": "HF_TOKEN",
                "value": YOUR_HF_TOKEN,
                "description": " Hugging Face token for logging purposes",
            },
            {
                "key": "LOGIN_CODES",
                "value": f"{name.lower()},admin",
                "description": "List of login codes for the users",
            },
        ],
        variables=[
            {
                "key": "MAX_NUM_SENTENCES",
                "value": "50",
            },
            {
                "key": "EVENT_LOGS_SAVE_FREQUENCY",
                "value": "50",
            },
            {
                "key": "EVENT_LOGS_HF_DATASET_ID",
                "value": f"{USER_OR_ORG}/grote-{name}",
            },
            {
                "key": "EVENT_LOGS_LOCAL_DIR",
                "value": "logs",
            },
            {
                "key": "ALLOWED_TAGS",
                "value": "minor,major",
            },
            {
                "key": "TAG_LABLES",
                "value": "Minor,Major",
            },
            {
                "key": "TAG_COLORS",
                "value": "#ffedd5,#fcd29a",
            }
        ]
    )
for name in names:
    print(f"URL: https://{USER_OR_ORG}-grote-{name}.hf.space\nLogin code: {name.lower()}")
```

## Editing flow with GroTE

1. Open the webpage of the GroTE interface
2. Insert the provided login code
3. Load one of the provided files
4. Press “📝 Start”
5. Perform the editing. If needed, use green checkmarks to remove highlights from a segment.
6. When all segments for the file are finished, click “✅ Done”
7. A message “Saving trial information. Don't close the tab until the download button is available!” will appear. Do not close the tab.
8. When the message “Saving complete! Download the output file by clicking the 'Download translations' button below.” appears, click “📥 Download translations” to download the edited files. The file will have the name `<LOGIN CODE>_<FILENAME>_output.txt`
9. Click “⬅️ Back to data loading” to return to the file loading page.
10. If needed, pause and take a break

Steps 2-9 are repeated for each file, which represents a standalone document with ordered segments.


## Future developments

While the current version of GroTE is functional, there are several improvements that could be made to enhance the user experience and functionality. I am unlikely to implement these changes in the near future, but I am happy to provide guidance and support to anyone interested in contributing to the project.

- Separate rendering logic for loading/editing tabs (see [ICLR 2024 Papers interface](https://huggingface.co/spaces/ICLR2024/update-ICLR2024-papers/blob/main/app.py) for an example)
- Use latest Gradio version to integrate features like [multi-page structure](https://www.gradio.app/guides/multipage-apps), [client-side functions](https://www.gradio.app/guides/client-side-functions), and [dynamic rendering](https://www.gradio.app/guides/dynamic-apps-with-render-decorator) of components.
- Enable restoring the previous state of edited sentences if matching filename and user are found in the logs in the past 24 hours (with a modal to enable starting from scratch).
- Possibly rethink logging format to reduce redundancy and improve readability.
- Add optional tab to visualize the editing process (e.g., Highlighted diffs between original and edited sentences, replay of editing process by looping `.then` with `time.sleep`, download scoped logs for single text).
- Change saving logic to use [BackgroundScheduler](https://www.gradio.app/guides/running-background-tasks)
- Change transition from editing to loading to preserve login code and possibly allow the pre-loading of several files for editing (would require a custom `FileExplorer` component to mark done documents).

## Questions and feedback

If you have any questions or feedback, please feel free to reach out to me at [gabriele.sarti996@gmail.com](mailto:gabriele.sarti996@gmail.com).
