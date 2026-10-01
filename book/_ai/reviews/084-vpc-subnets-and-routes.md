# Independent review — Chapter 84

Reviewer: write_operations (independent of write_delivery)
Review date: 2026-10-01
Verdict: approved
Reviewed body SHA256: 204e08aebbd720c12e399650f41785739258cca7befdc2c557f890719feb26cc

## Scope and substantive findings

Entire finished manuscript read, including prose, commands/configuration, examples, recovery reasoning, exercises, distribution treatment, assumptions and published verification limits. No unresolved material findings.

Main route-table implicit fallback, address overlap and rollout address use, IGW/public IPv4 requirements, endpoints versus authorization and current regional NAT caveat are correct. Isolated VPC/subnet lab captures returned IDs, supplies existing authorized context/account preflight, does not imply packet verification, and handles partial creation and cleanup dependencies.

The transient publication sentence about pending review was removed by its owning author before this reviewed hash. No runtime claim was introduced by review.

## Source inspection

Primary documentation inspected for this batch includes Terraform state-push safeguards, AWS CLI Identity Center, IAM evaluation/custom simulation, VPC route/SG/NACL/NAT behavior, EC2 run-instances/IMDSv2, EBS snapshot restoration, S3 versioning/upload and Route53/ACM/ALB/CloudFormation behavior. Chapter-specific reference: [official documentation](https://docs.aws.amazon.com/vpc/latest/userguide/vpc-nat-gateway.html). Exact scope is the claims and examples described above, not all provider offerings or account-specific configuration.

## Validation and limits

Actual `python3 tools/check_book.py --chapters 080-089` invocation passed shell26, Python1, JSON4, YAML1 syntax/parsing and global local-link inspection with no errors or warnings. This reviewer performed no AWS login/API call, resource provisioning, Terraform state operation, cloud-init/SSM integration, storage restore, policy evaluation execution or packet/TLS test. Syntax parsing is not schema, authorization, durability or runtime proof. Installed release, account, region, actual permissions/pricing and live resource integration remain reader-side validation requirements stated in the chapter.

## Next step

Coordinator may promote this exact reviewed body after normal shared consistency validation. Any prose/example change requires a reviewed delta and refreshed body hash.
