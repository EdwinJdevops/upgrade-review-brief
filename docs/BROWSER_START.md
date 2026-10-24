> Historical working notes. Current submission claims require evidence in [SUBMISSION_FACTS.md](../SUBMISSION_FACTS.md).

# Run and submit from a browser

Repository: https://github.com/EdwinJdevops/upgrade-review-brief

[Successful test and CPU model demonstration](https://github.com/EdwinJdevops/upgrade-review-brief/actions/runs/39942834494) ; 45 tests passed, followed by five actual BGE evaluations and a generated report with no passages omitted. Source/model files were checked against pinned identities. No WSL or model API key was required.

## Inspect or repeat the demonstration

1. Open the linked run summary and read the generated review brief.
2. To repeat it, open Actions, select **Test and demonstrate upgrade review**, choose **Run workflow**, enable `run_model`, and run on main.
3. Normal pushes run fast tests only. A main-branch commit containing `[model-demo]` also explicitly requests CPU inference.

Standard public-repository GitHub-hosted runners are used. No larger runner, provider API, artifact upload or persistent model cache is configured.

## Finish the DEV entry

DEV_SUBMISSION_DRAFT.md now has the verified repository and successful run links. Review its explanation and limitations, then copy it into the official Week 3 submission template at https://dev.to/challenges/hacktoberfest-week3-2026-10-19 . Retain `devchallenge` and `hf26challenge` tags. A real local browser demonstration is now recorded at docs/demo/browser-demo.mp4. The live service is now available at https://upgrade-review-brief.onrender.com; no DEV submission has been published.

The proposed partner entry uses the explicitly described GitHub Actions option in Best Use of GitHub Copilot. Copilot itself was not used. Render now hosts the actual inference runtime. Backboard, Tinker and the event .tech domain remain unused. Judges decide category acceptance and awards; a successful workflow is not a prize result.

The official cutoff is October 25, 2026 at 11:59 PM PDT. The challenge permits AI coding help while requiring an essential open-source AI role in the product. Do not describe relevance scores as upgrade safety confidence or unit tests as customer validation.

## Browser app and Render

The application now has a browser interface for the included example and sanitized uploads. See RENDER_DEPLOYMENT.md and CONTEST_READINESS.md. The Render connection, service creation and public functional checks are complete. Remaining credits are unverified through MCP. The recorded video is a valid type of demo requested by the contest, but the submission post must still be published and verified.
