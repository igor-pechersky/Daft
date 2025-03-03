# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "PyGithub",
#   "boto3",
# ]
# ///

import argparse
import json
from typing import Optional

import git_utils
import github

TOTAL_NUMBER_OF_QUESTIONS = 22


def run(
    branch_name: Optional[str],
    questions: Optional[str],
    scale_factor: int,
    num_partitions: int,
    cluster_profile: str,
    env_vars: Optional[str],
):
    branch_name, _ = git_utils.get_name_and_commit_hash(branch_name)

    expanded_questions = git_utils.parse_questions(questions, TOTAL_NUMBER_OF_QUESTIONS)
    print(
        f"Running scale-factor of {scale_factor}GB with {num_partitions} partitions on questions: {', '.join(map(str, expanded_questions))}"
    )
    args_as_list = [
        f"--question-number={q} --parquet-folder=s3://eventual-dev-benchmarking-fixtures/uncompressed/tpch-dbgen/{scale_factor}_0/{num_partitions}/parquet/"
        for q in expanded_questions
    ]
    entrypoint_args = json.dumps(args_as_list)

    workflow = git_utils.repo.get_workflow("run-cluster.yaml")
    git_utils.dispatch(
        workflow=workflow,
        branch_name=branch_name,
        inputs={
            "cluster_profile": cluster_profile,
            "working_dir": "benchmarking/tpch",
            "entrypoint_script": "ray_job_runner.py",
            "entrypoint_args": entrypoint_args,
            "env_vars": env_vars,
        },
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ref", type=str, required=False, help="The branch name to run on")
    parser.add_argument("--questions", type=str, required=False, help="A comma separated list of questions to run")
    parser.add_argument(
        "--scale-factor",
        choices=[2, 10, 100, 1000],
        type=int,
        required=False,
        default=2,
        help="The scale factor to run on",
    )
    parser.add_argument("--num-partitions", type=int, required=True, help="The number of partitions")
    parser.add_argument(
        "--cluster-profile",
        choices=["debug_xs-x86", "medium-x86", "benchmarking-arm"],
        type=str,
        required=False,
        help="The ray cluster configuration to run on",
    )
    parser.add_argument(
        "--env-var",
        type=str,
        action="append",
        required=False,
        help="Environment variable in the format KEY=VALUE. Can be specified multiple times.",
    )
    parser.add_argument("--verbose", action="store_true", help="Verbose debugging")
    args = parser.parse_args()

    if args.verbose:
        github.enable_console_debug_logging()

    env_vars = None
    if args.env_var:
        list_of_env_vars: list[str] = args.env_var
        for env_var in list_of_env_vars:
            if "=" not in env_var:
                raise ValueError("Environment variables must in the form `KEY=VALUE`")
        env_vars = ",".join(list_of_env_vars)

    run(
        branch_name=args.ref,
        questions=args.questions,
        scale_factor=args.scale_factor,
        num_partitions=args.num_partitions,
        cluster_profile=args.cluster_profile,
        env_vars=env_vars,
    )
