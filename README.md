# GroTE: Groningen Translation Environment 🐮

## Accessing the GroTE demo

An online GroTE demo is available at [https://grote-app.hf.space](https://grote-app.hf.space). The demo will log events to the private repository [grote/grote-logs](https://huggingface.co/datasets/grote/grote-logs).

## Running GroTE locally

1. Install requirements: `pip install -r requirements.txt`.
2. Make sure you have a local `npm` installation available to run the front-end.
3. Run `grote` in your command line to start the server.
4. Visit http://127.0.0.1:7860 to access the demo. By default, logs are written to the local `logs` directory, which is synchronized with the repository [grote/grote-logs](https://huggingface.co/datasets/grote/grote-logs).

## TODOs for before the QE4PE study

- [x] Add a JS check to prevent users from accidentally closing the tab while editing.
- [x] Remove trailing spaces in parsed texts.
- [x] Make Ctrl+C on source sentences a customizable option (default: allowed).
- [x] Minimize HF bar by default with `header: mini` in README.

## TODOs for after QE4PE study

- [ ] Separate rendering logic for loading/editing tabs (see [ICLR 2024 Papers interface](https://huggingface.co/spaces/ICLR2024/update-ICLR2024-papers/blob/main/app.py) for an example)
- [ ] Enable restoring the previous state of edited sentences if matching filename and user are found in the logs in the past 24 hours (modal to enable starting from scratch).
- [ ] Possibly rethink logging format to reduce redundancy and improve readability.
- [ ] Add optional tab to visualize the editing process (e.g., Highlighted diffs between original and edited sentences, replay of editing process by looping `.then` with `time.sleep`, download scoped logs for single text).
- [ ] Change saving logic to use [BackgroundScheduler](https://www.gradio.app/guides/running-background-tasks)
- [ ] Change transition from editing to loading to preserve login code and possibly allow the pre-loading of several files for editing (would require custom `FileExplorer` to mark done documents).
- [ ] Write tutorial on how to
