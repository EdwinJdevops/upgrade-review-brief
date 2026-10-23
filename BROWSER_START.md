# Finish the entry from a browser

The project is a local-model upgrade review brief. It compares selected Deployment fields, orders migration-note passages with BGE and preserves missing evidence. The CPU inference demonstration can run on a standard GitHub-hosted runner. No WSL, user-side model download, GPU or model API key is required for that path.

## First action

Create a public repository named `upgrade-review-brief` at https://github.com/new and share its exact URL in this conversation. Repository creation is not exposed by the connected GitHub tools. The account was verified as EdwinJdevops; the requested repository returned 404 on October 23, so its availability is not established. Do not put this project in a repository belonging to another hackathon experiment.

The prepared files belong at repository root. The workflow file must be `.github/workflows/review.yml`, not nested under the archive's `helm-upgrade-review` folder. A README on the new repository is fine; existing files will be inspected before an implementation branch is created.

## After the code has been committed

1. Open the repository's Actions tab and inspect the test run for that exact commit. Resolve any failed step before declaring CI passed.
2. Select **Test and demonstrate upgrade review**, choose **Run workflow**, enable `run_model`, and run it on the implementation branch. The heavier job is optional and never runs on normal pushes or pull requests.
3. Open the run summary after the model job completes. It contains the actual generated review brief. Logs record the model identity and the number of model calls. Record or demonstrate this successful run in the submission.
4. Complete `DEV_SUBMISSION_DRAFT.md` with the verified repository link and the actual run/video link. The draft deliberately does not contain invented public URLs. Use the official DEV submission template and retain `devchallenge` and `hf26challenge` tags.

Standard GitHub-hosted runners in public repositories are free under GitHub's published billing documentation. Larger runners are outside this plan. Account or organization Actions policies can still prevent execution; no GitHub run has been performed for this project yet. No artifact upload or persistent model cache is configured.

## What is actually ready

- Source, source-identity checks, model downloader and demonstration inputs recovered from the previously saved package.
- 45 tests re-executed successfully on October 23 in the assistant's environment.
- October 20 local model results and clean-package replay preserved under `verification/`.
- Browser-triggered CI/model workflow prepared and parsed locally. GitHub execution is pending repository access.
- DEV article draft and concrete recording sequence prepared. No article, video, badge or prize is claimed as completed.

## Rules checked October 23

The challenge is weekly; Week 3 ends October 25, 2026 at 11:59 PM PDT. AI assistance with code is allowed. The product needs an essential open-source AI component. This project actually uses open model weights for relevance ranking; final judging remains with the organizers. A valid submission can receive the published completion badge, while winning is a separate outcome. The page does not establish an automatic certificate for this prototype.

No sponsor integration has been completed. The entry can compete for the overall category without partner technology. List a partner category only after genuine use has been implemented and demonstrated. Do not spend time on an unrelated integration or claim that every offer must be consumed. One submission can win only once per challenge.

Sources:
- https://dev.to/challenges/hacktoberfest-week3-2026-10-19
- https://docs.github.com/en/actions/concepts/billing-and-usage
- https://huggingface.co/BAAI/bge-reranker-base
