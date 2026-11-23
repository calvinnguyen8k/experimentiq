# Two-minute ExperimentIQ live demo

Submission recording: `output/demo/experimentiq-live-demo.webm`. Captured from
https://experimentiq-omega.vercel.app in a fresh unauthenticated Chromium context
on 23 November 2026. All three AI stages called real OpenAI; Python calculated the
sample size. There were no provider mocks. Captions were added by the recording
script to explain the live actions. The video is silent, with readable captions.

| Time | Action |
|---|---|
| 0:00-0:07 | Introduce ExperimentIQ and the live URL. |
| 0:07-0:17 | Load the complete fictional spending example. |
| 0:17-0:31 | Extract facts and explain provenance. |
| 0:31-0:48 | Generate and acknowledge the proposed design. |
| 0:48-0:59 | Review and confirm numerical assumptions. |
| 0:59-1:13 | Calculate and show 1,570 per arm, 3,140 total. |
| 1:13-1:34 | Request and inspect independent AI risk review. |
| 1:34-1:44 | Inspect unresolved assumptions. |
| 1:44-1:53 | Acknowledge risks and download the Markdown report. |
| 1:53-2:00 | Edit SD to demonstrate blocking and downstream invalidation. |

`output/demo/live-demo-evidence.json` records event times, model metadata and the
four successful API request IDs. `output/demo/live-demo-report.md` is the actual
download from this recording. The source capture was trimmed to two minutes;
app responses and calculations were not substituted.

The earlier `experimentiq-walkthrough.webm` uses explicitly labelled fixture
screenshots. It is retained as a historical walkthrough and is not the submission
recording.
