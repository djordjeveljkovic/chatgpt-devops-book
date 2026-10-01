---
book: The Complete DevOps Engineering Book
volume: 9
volume_title: "AWS Foundations"
chapter: 89
title: "Route 53, Certificates and Load Balancers"
slug: route-53-certificates-and-load-balancers
status: complete
summary: ../../_ai/chapter-summaries/089-route-53-certificates-and-load-balancers.md
---

# Chapter 89 — Route 53, Certificates and Load Balancers

## DNS records and routing policies

Publishing DispatchDesk requires a chain of independently observable boundaries: a hostname resolves, a client reaches a listener, TLS authenticates the intended name, the listener selects a backend, and the backend accepts work safely. A green DNS change cannot prove all five. Summit can use Route 53, ACM and an Application Load Balancer for this chain; Harbor can keep its VPS reverse proxy, and Atlas can use its maintained Kubernetes gateway. The contract is shared even though the implementation differs.

Read [DNS](../03-networking-and-traffic/023-dns-from-resolver-to-authority.md) and [TLS](../03-networking-and-traffic/025-tls-certificates-and-trust.md) for the underlying mechanisms. A hosted zone is an authoritative configuration boundary, but creating one does not automatically delegate an existing domain to it. Registrar or parent-zone delegation must point at the correct authoritative servers. Multiple hosted zones with the same domain name can exist; changing the unused one produces a convincing control-plane success while customers continue seeing old answers.

A Route 53 alias can point an A record at an AWS load balancer without copying its changing IP addresses. It also supports the zone apex where an ordinary CNAME is unsuitable. [AWS's load-balancer routing guide](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/routing-to-elb-load-balancer.html) documents the alias relationship. Keep the hosted zone's ID separate from the load balancer's canonical hosted-zone ID: they serve different fields in the record definition.

Begin with simple routing when there is one accepted endpoint. Weighted, failover, latency and other policies need explicit traffic and failure requirements, health assumptions and rollback plans. DNS routing decisions are observed through caches, not instantly enforced on every active connection. A rollback therefore needs the old endpoint to remain usable during the transition. Do not implement a database migration by assuming a DNS change synchronously moves all clients.

## ACM and listener integration

An HTTPS listener needs a certificate covering the client-facing hostname and a security policy that meets the intended TLS compatibility and security requirements. ACM DNS validation provides records proving domain control; it is separate from the application alias. Keep validation records under ownership so renewal can continue. [ACM's DNS validation guide](https://docs.aws.amazon.com/acm/latest/userguide/dns-validation.html) describes the generated CNAME and ongoing renewal conditions. Do not fabricate a validation token or assume a wildcard covers every nested hostname.

For this regional ALB example, supply an issued ACM certificate usable by the listener in its region and account, covering the exact lab hostname. Inspect its status, names, expiry and attachment before deployment. A certificate's ARN is not proof it is issued or appropriate. DNS validation failures often come from writing the wrong zone or a provider appending the domain twice to a full record name. Inspect authoritative answers for the actual returned validation record rather than repeatedly requesting new certificates.

Choose a supported ALB security policy after inspecting available policies and the requirements of actual clients. The template accepts its name as a parameter instead of embedding a tutorial policy that silently ages. [The listener guide](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/load-balancer-listeners.html) explains listeners and their actions. TLS terminates at the ALB here; forwarding HTTP within the VPC is an explicit example choice, not a claim that all internal traffic is trustworthy. A production requirement for backend encryption needs its own target protocol and trust review.

## A complete endpoint definition

Save this complete CloudFormation template as `endpoint.yaml`. It creates an internet-facing IPv4 ALB, HTTPS listener, empty IP target group on DispatchDesk's port 8080, and a lab DNS alias. It creates no application targets, certificate, security group or network. An empty target group cannot serve DispatchDesk. The definition prepares the boundary for the [ECS service chapter](../10-aws-production-services/093-ecs-and-fargate-services.md), which owns task registration and replacement.

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: Disposable DispatchDesk endpoint boundary without targets
Parameters:
  VpcId:
    Type: AWS::EC2::VPC::Id
  PublicSubnetOne:
    Type: AWS::EC2::Subnet::Id
  PublicSubnetTwo:
    Type: AWS::EC2::Subnet::Id
  LoadBalancerGroup:
    Type: AWS::EC2::SecurityGroup::Id
  CertificateArn:
    Type: String
  SecurityPolicy:
    Type: String
  HostedZoneId:
    Type: String
  RecordName:
    Type: String
Resources:
  Endpoint:
    Type: AWS::ElasticLoadBalancingV2::LoadBalancer
    Properties:
      Scheme: internet-facing
      Type: application
      IpAddressType: ipv4
      Subnets:
        - Ref: PublicSubnetOne
        - Ref: PublicSubnetTwo
      SecurityGroups:
        - Ref: LoadBalancerGroup
      Tags:
        - Key: Purpose
          Value: temporary-lab
  OrdersTargets:
    Type: AWS::ElasticLoadBalancingV2::TargetGroup
    Properties:
      VpcId:
        Ref: VpcId
      TargetType: ip
      Protocol: HTTP
      Port: 8080
      HealthCheckPath: /readyz
      HealthCheckPort: traffic-port
      Matcher:
        HttpCode: '200'
      Tags:
        - Key: Purpose
          Value: temporary-lab
  SecureListener:
    Type: AWS::ElasticLoadBalancingV2::Listener
    Properties:
      LoadBalancerArn:
        Ref: Endpoint
      Protocol: HTTPS
      Port: 443
      SslPolicy:
        Ref: SecurityPolicy
      Certificates:
        - CertificateArn:
            Ref: CertificateArn
      DefaultActions:
        - Type: forward
          TargetGroupArn:
            Ref: OrdersTargets
  EndpointRecord:
    Type: AWS::Route53::RecordSet
    Properties:
      HostedZoneId:
        Ref: HostedZoneId
      Name:
        Ref: RecordName
      Type: A
      AliasTarget:
        DNSName:
          Fn::GetAtt: [Endpoint, DNSName]
        HostedZoneId:
          Fn::GetAtt: [Endpoint, CanonicalHostedZoneID]
        EvaluateTargetHealth: false
Outputs:
  LoadBalancerArn:
    Value:
      Ref: Endpoint
  TargetGroupArn:
    Value:
      Ref: OrdersTargets
  EndpointName:
    Value:
      Ref: RecordName
```

The public subnets must belong to the specified VPC and distinct supported Availability Zones, with the internet paths and address capacity required by the ALB. The supplied group must allow intended client TCP 443 ingress and the intended backend/health-check egress. Application groups must accept port 8080 from it when actual targets exist. [Chapter 85](085-security-groups-and-network-acls.md) owns those network permissions. The template intentionally does not open host administration ports.

`/readyz` means the application can safely accept work; `/healthz` only establishes process health. A status matcher of 200 makes the acceptance signal precise. Broader success ranges can accidentally count login redirects or error pages as ready. The target type `ip` supports the later task-network interface model. `EvaluateTargetHealth: false` avoids implying this single simple alias performs health-based DNS failover; backend health remains the ALB's responsibility. Review the [target-group](https://docs.aws.amazon.com/AWSCloudFormation/latest/TemplateReference/aws-resource-elasticloadbalancingv2-targetgroup.html) and [record-set](https://docs.aws.amazon.com/AWSCloudFormation/latest/TemplateReference/aws-resource-route53-recordset.html) schema when adapting these choices.

## Publishing and diagnosing the boundary

This optional deployment changes a real DNS name and creates a billable ALB. Use a dedicated lab hostname in a domain you control, with no existing record or customer dependency. Do not use a production hostname or a documentary domain you do not own. Review [load-balancer pricing](https://aws.amazon.com/elasticloadbalancing/pricing/) and related DNS/certificate offerings; no free-tier promise is made. Establish cleanup ownership before deployment. No AWS operation below was executed during authoring.

Use AWS CLI v2 from an ordinary Bash workstation user on Ubuntu 24.04 LTS, Fedora 44 or RHEL 9. Complete [Chapter 82's account preflight](082-aws-cli-and-identity-sessions.md). The operator needs approved CloudFormation and resource permissions, including the intended Route 53 change. Existing network, certificate and hosted-zone ownership must authorize this lab. Review available security policies with `elbv2 describe-ssl-policies` in the chosen region and inspect the certificate with `acm describe-certificate` before entering their real values.

```bash
set -euo pipefail
lab_profile=dispatchdesk-sandbox
lab_region=eu-west-1
lab_stack=dispatchdesk-endpoint-lab
read -r -p 'Verified VPC ID: ' lab_vpc
read -r -p 'First approved public subnet: ' lab_subnet_one
read -r -p 'Second approved public subnet: ' lab_subnet_two
read -r -p 'Approved ALB security-group ID: ' lab_group
read -r -p 'Issued matching ACM certificate ARN: ' lab_certificate
read -r -p 'Approved supported ALB TLS policy name: ' lab_tls_policy
read -r -p 'Authoritative public hosted-zone ID: ' lab_zone
read -r -p 'Unused owned lab FQDN: ' lab_name
aws --profile "$lab_profile" --region "$lab_region" --no-cli-pager   cloudformation create-change-set --stack-name "$lab_stack"   --change-set-name initial-endpoint --change-set-type CREATE   --template-body file://endpoint.yaml --parameters   "ParameterKey=VpcId,ParameterValue=$lab_vpc"   "ParameterKey=PublicSubnetOne,ParameterValue=$lab_subnet_one"   "ParameterKey=PublicSubnetTwo,ParameterValue=$lab_subnet_two"   "ParameterKey=LoadBalancerGroup,ParameterValue=$lab_group"   "ParameterKey=CertificateArn,ParameterValue=$lab_certificate"   "ParameterKey=SecurityPolicy,ParameterValue=$lab_tls_policy"   "ParameterKey=HostedZoneId,ParameterValue=$lab_zone"   "ParameterKey=RecordName,ParameterValue=$lab_name"
aws --profile "$lab_profile" --region "$lab_region" --no-cli-pager   cloudformation wait change-set-create-complete   --stack-name "$lab_stack" --change-set-name initial-endpoint
aws --profile "$lab_profile" --region "$lab_region" --no-cli-pager   cloudformation describe-change-set   --stack-name "$lab_stack" --change-set-name initial-endpoint
```

Creation of the change set prepares a reviewable change; execution creates the endpoint resources. Inspect the complete parameter list and four intended resources. A change-set success is not permission or proof that the eventual DNS and certificate combination will work. After approving that exact plan within your lab authorization:

```bash
aws --profile "$lab_profile" --region "$lab_region" --no-cli-pager   cloudformation execute-change-set   --stack-name "$lab_stack" --change-set-name initial-endpoint
aws --profile "$lab_profile" --region "$lab_region" --no-cli-pager   cloudformation wait stack-create-complete --stack-name "$lab_stack"
aws --profile "$lab_profile" --region "$lab_region" --no-cli-pager   cloudformation describe-stacks --stack-name "$lab_stack" --output json
curl --silent --show-error --max-time 10 --output /dev/null   --write-out 'HTTP status: %{http_code}\n' "https://$lab_name/readyz"
```

The curl request retains normal certificate verification. An HTTP error from the empty target group is expected; a 200 application readiness claim would be incorrect. Distinguish DNS resolution failure, TLS failure, connection timeout and an HTTP response. Inspect stack outputs to obtain the actual target-group ARN and use `elbv2 describe-target-health` for backend evidence. Before adding real tasks, the target list should be empty. When later tasks are registered but unhealthy, inspect reason codes, actual listening address, port, readiness response and group permissions rather than disabling health checks.

A classic failed assumption is that a valid certificate for one hostname covers the lab name. If TLS fails before HTTP, compare the requested hostname with the certificate's subject alternative names and listener attachment. Correct the certificate or intended name through the owning definition. Using curl's insecure option would conceal the boundary that customers rely on. If DNS instead resolves the previous endpoint, inspect authoritative delegation and caches before changing the application.

Remove the optional lab through its stack, which owns the alias and ALB resources:

```bash
aws --profile "$lab_profile" --region "$lab_region" --no-cli-pager   cloudformation delete-stack --stack-name "$lab_stack"
aws --profile "$lab_profile" --region "$lab_region" --no-cli-pager   cloudformation wait stack-delete-complete --stack-name "$lab_stack"
rm -- endpoint.yaml
```

Confirm the lab alias and load balancer are removed and investigate delete failures. Existing certificate, zone, security group and subnets remain owned outside the stack; do not delete them as incidental cleanup. Preserve ACM validation records needed by other certificate uses. A failed create or wait also needs stack-event inspection and cleanup of any resources that actually survived.

## Exercises and answer guidance

1. DNS resolves and curl reports a certificate-name mismatch. Which boundary should be investigated first? The hostname-to-certificate relationship and listener certificate, before backend health.
2. Why does this template not prove DispatchDesk readiness? It contains an empty target group and no application. Infrastructure publication and service acceptance are distinct evidence.
3. What differs between the alias's hosted-zone IDs? The record lives in your authoritative zone; the target identifies the ALB's canonical AWS zone.
4. Why preserve the old endpoint during DNS rollback? Cached answers and existing connections can continue directing clients there during convergence.

Review questions: who owns authoritative delegation, what renews the certificate, which policy governs TLS, and what exact response establishes readiness before customer routing?

## Verification and primary sources

Official Route 53, ACM, ALB, CloudFormation and CLI documentation was inspected on 2026-10-01. No domain, certificate, stack, listener or DNS record was changed. Local YAML parsing is not CloudFormation schema validation, and no TLS or target-registration integration was exercised.

Additional references: [load-balancer resource](https://docs.aws.amazon.com/AWSCloudFormation/latest/TemplateReference/aws-resource-elasticloadbalancingv2-loadbalancer.html), [listener resource](https://docs.aws.amazon.com/AWSCloudFormation/latest/TemplateReference/aws-resource-elasticloadbalancingv2-listener.html), [SSL-policy inspection](https://docs.aws.amazon.com/cli/latest/reference/elbv2/describe-ssl-policies.html), [certificate inspection](https://docs.aws.amazon.com/cli/latest/reference/acm/describe-certificate.html), and [target-health inspection](https://docs.aws.amazon.com/cli/latest/reference/elbv2/describe-target-health.html).
