# Chapter 105 continuation

Status: complete

## Written material
Selector and EndpointSlice behavior; ClusterIP/NodePort/LoadBalancer/headless/selectorless/ExternalName distinctions; Service port mapping and DNS names; layered diagnosis of empty backend sets, DNS and connection failures; temporary diagnostic Pod and cleanup; exercises with answer guidance.

## Exact next section
None. Independently approved; continue to the next unfinished chapter.

## Concepts and terminology
Service, ClusterIP, selector, targetPort, EndpointSlice, ready/serving/terminating endpoint, headless Service, ExternalName, cluster DNS, search path, SRV record.

## Examples and cross-references
Service targets Chapter 104 Deployment; commands assume context `kind-dispatchdesk` and namespace `production`. Diagnostic Pod uses BusyBox example tag and is not run. Links to Chapters 102 and 104.

## Open threads
None known. Cluster DNS domain, CNI, Service proxy and policy behavior remain environment-specific as described in the chapter.

## Verification
Official Kubernetes Service, EndpointSlice, DNS and debug documentation inspected 2026-10-04. No cluster queries or network requests performed.
