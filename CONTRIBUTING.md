# Contributing Guidelines

Pull requests, bug reports, and other contributions are welcome. This guide explains
how to contribute to HexaMSH and help us maintain a welcoming project.

## Code of Conduct

Please review our [Code of Conduct](CODE_OF_CONDUCT.md). It applies to everyone
participating in the project.

## Issues and security reports

Before opening an issue, check that you are using the latest version and search
existing issues for duplicates. For bug reports, include steps to reproduce the
problem, relevant error output, your operating system, and the Python and HexaMSH
versions. Feature requests should explain the problem they would solve and the
expected outcome.

Do not report security vulnerabilities in a public issue. Report them privately
through the [Michelin Open Source contact channel](https://opensource.michelin.io).

## Pull requests

For substantial changes, open or join an issue first to discuss the proposed approach.
Keep each pull request focused on one change, describe its motivation, and include
tests or documentation updates where appropriate. Follow the existing Python style
and naming conventions; the project configures Black, isort, and Pylint in
`pyproject.toml`.

Run the relevant checks before submitting. The Gmsh replay tests can be run from the
repository root with:

```shell
python hexamsh/tests/test.py
```

Please address review feedback and any CI failures.

## AI-assisted contributions

AI tools may be used to assist with contributions, including code, tests,
documentation, images, issue reports, and commit messages. Their use does not change
the contribution process or lower the standards applied during review. The human
contributor remains the author and is fully responsible for everything they submit.

If you use an AI tool when preparing a contribution:

- **Understand and review the result.** Review every AI-assisted change and make
  sure you can explain, maintain, and defend it. Do not submit content that you do
  not understand.
- **Verify quality and safety.** Check the result for correctness, security,
  accessibility, bias, and consistency with the project's conventions. Run the
  relevant tests and validation tools. AI output must not be treated as evidence
  that a change is correct.
- **Respect licenses and provenance.** Ensure that the contribution is compatible
  with the project's license and does not reproduce third-party material without
  the necessary rights and attribution. You remain responsible for establishing
  the provenance of the submitted content.
- **Protect sensitive information.** Do not provide credentials, personal data,
  confidential information, embargoed vulnerabilities, or other restricted project
  material to an AI service unless its use for that information has been explicitly
  authorized.
- **Certify the contribution yourself.** An AI tool must not add a `Signed-off-by`
  line or otherwise certify the Developer Certificate of Origin. Only the human
  contributor may do so, after reviewing the complete contribution and confirming
  that they have the right to submit it.
- **Disclose material assistance.** When an AI tool materially generates or
  modifies submitted content, add an `Assisted-by` trailer to the commit message.
  Routine spelling correction, formatting, search, or completion that does not
  materially shape the contribution does not require a trailer.

Name the tool or agent and the specific model version when known. Specialized
analysis tools may be listed after the model; ordinary development tools such as
editors, compilers, and Git should not be listed.

```text
Assisted-by: TOOL_OR_AGENT
```

Maintainers may ask contributors to explain, revise, or replace AI-assisted content
that cannot be adequately reviewed or whose provenance is unclear. This AI section
policy is adapted from the Linux kernel's
[guidance for AI coding assistants](https://docs.kernel.org/process/coding-assistants.html).

## Certificate of Origin

By making a contribution to this project, you certify that:

> 1. The contribution was created in whole or in part by you and you have the right
>    to submit it under the open source license indicated in the file; or
> 1. The contribution is based upon previous work that, to the best of your
>    knowledge, is covered under an appropriate open source license and you have
>    the right under that license to submit that work with modifications, whether
>    created in whole or in part by you, under the same open source license
>    (unless you are permitted to submit under a different license), as indicated
>    in the file; or
> 1. The contribution was provided directly to you by some other person who
>    certified (1), (2), or (3) and you have not modified it; or
> 1. You understand and agree that this project and the contribution are public and
>    that a record of the contribution (including personal information you submit
>    with it, including your sign-off) is maintained indefinitely and may be
>    redistributed consistent with this project or the applicable open source
>    license(s).

This text is based on the
[_Developer's Certificate of Origin 1.1_](https://developercertificate.org/).
