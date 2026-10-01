---
book: The Complete DevOps Engineering Book
volume: 2
volume_title: "Linux and Automation"
chapter: 13
title: "Text Processing and Pipelines"
slug: text-processing-and-pipelines
status: complete
summary: ../../_ai/chapter-summaries/013-text-processing-and-pipelines.md
---

# Chapter 13 — Text Processing and Pipelines

## Why this matters

Harbor needs to know which notification failures deserve attention. A developer searches a log, counts a few matching lines, and reports that retries are rare. Yet the search read yesterday's file, its upstream command failed, and the count included a debug message containing the word `failed`. Each command ran; the conclusion was wrong.

Text tools are useful because they let you inspect evidence without building a new application. Their reliability depends on a contract: what constitutes a record, which fields mean what, how errors travel, and what time interval the input covers. A pipeline is a small program with those obligations. This chapter develops that program from streams to a repeatable DispatchDesk report.

The examples use Bash and common Linux utilities on Ubuntu 24.04 LTS, Fedora 44, and RHEL 9. They avoid distribution-specific log paths. Ubuntu may provide a different default awk implementation from Fedora or RHEL; the awk example uses basic portable features. Install optional tools through your distribution's trusted repositories using the package workflow in Chapter 17. Confirm `jq --version` before the JSON exercise; its examples use established options available in commonly packaged versions rather than new jq 1.8 features.

## Three streams, three purposes

A command normally inherits standard input, standard output, and standard error: file descriptors 0, 1, and 2. Input supplies records. Output carries results that another program can consume. Error carries diagnostics. They may initially point at the same terminal, but that does not make them the same stream.

This separation lets a collector emit machine-readable JSON on stdout while explaining a permission failure on stderr. Redirecting only stdout preserves that distinction:

```bash
printf 'accepted=3\n' > result.txt
printf 'sample diagnostic\n' >&2
cat < result.txt
```

Run this only inside a disposable practice directory. `>` creates or truncates its destination before the command runs. `>>` appends. `<` opens an input file. None of these operators validates the content. Redirecting a failing producer into a valuable existing report can destroy the previous evidence before the failure becomes apparent.

Order matters because redirections are applied from left to right. `command > combined.txt 2>&1` first sends stdout to the file, then makes stderr refer to that same destination. `command 2>&1 > results.txt` first makes stderr refer to the original stdout destination, then changes stdout alone. In the latter case diagnostics still reach the original terminal. `2>&1` duplicates a descriptor destination; it does not establish a permanent symbolic link between descriptor numbers. These are documented Bash behaviors, not properties of a particular terminal. [Bash reference manual](https://man7.org/linux/man-pages/man1/bash.1.html).

Do not merge diagnostics into structured records merely to capture everything. A traceback inserted into a JSON stream makes parsing fail; worse, a loose text filter may quietly count it as data. Keep an error file beside the raw result when collecting incident evidence. Restrict both if they contain customer identifiers, and choose a retention period. Chapter 8's execution context and recovery discipline applies even to read-only investigations that write local evidence.

## A pipe connects processes, not completed files

In `producer | consumer`, the producer's stdout becomes the consumer's stdin. The shell starts the pipeline's processes without waiting for the producer to finish the complete dataset. The kernel buffers a limited quantity of bytes. A slow consumer eventually makes a writing producer wait; this is backpressure. It prevents unlimited buffering inside the pipe but does not guarantee that an application upstream has bounded its own queues.

A pipe transports bytes. Newline boundaries are a convention adopted by these tools. One write need not become one read, and neither operation implies one application event. A JSON object spanning several lines cannot safely be treated as several independent log records. Likewise, two events on one line violate a line-oriented schema.

If a consumer exits early, a later producer write may receive a broken-pipe error or SIGPIPE. That is sometimes expected: `head` deliberately stops after a bounded sample. It can also interrupt a producer doing useful work. Avoid adding `head` to a command with side effects merely to reduce output. Sampling a saved evidence file has a different risk from terminating a live producer.

Pipeline exit status needs explicit attention. Bash normally reports the last command's status. Thus a failing reader followed by a successful counter can look successful. With `set -o pipefail`, Bash reports a nonzero status when a stage fails, using the rightmost failing stage's status. This helps but does not explain which stage failed. Bash's `PIPESTATUS` array records the individual statuses; capture it immediately because the next command replaces it. [Bash pipeline and parameter documentation](https://man7.org/linux/man-pages/man1/bash.1.html).

```bash
bash -c 'false | wc -l; printf "pipeline=%s\n" "$?"'
bash -o pipefail -c 'false | wc -l; printf "pipeline=%s\n" "$?"'
bash -c 'false | wc -l; codes=("${PIPESTATUS[@]}"); printf "stages: %s\n" "${codes[*]}"'
```

The counter prints zero in both first examples. Their pipeline statuses differ: zero without pipefail, nonzero with it. The third reports the failed first stage and successful second stage. A zero count therefore means nothing until you know that input collection succeeded. Search tools also have meaningful nonzero statuses: grep uses a no-match status that differs from an execution error. Decide whether no matches are an expected empty result before enforcing a blanket failure rule.

## Choose the parser from the record format

Use `grep -F` for a literal string and regular expressions when pattern semantics are intended. Quoting protects a pattern from shell expansion; it does not turn a regex into a literal. `grep -F -- 'order[17]' file` searches for brackets literally. Avoid inferring severity from a substring: a line saying `failed_count=0` still contains `failed`.

For deliberately simple delimiter-separated records, awk can select fields and aggregate values. Its default whitespace splitting is inappropriate when spaces belong inside fields. Set the delimiter explicitly and document exclusions. This tab-separated fixture has exactly four fields: event, outcome, order identifier, and latency in milliseconds. Values contain no tabs or embedded newlines.

```bash
cat > events.tsv <<'EOF'
notification	sent	order-1	40
notification	retry	order-2	120
order	accepted	order-3	12
notification	retry	order-4	200
EOF
awk -F '\t' '
  NF != 4 { bad++; next }
  $1 == "notification" && $2 == "retry" {
    count++; total += $4
  }
  END {
    if (bad) {
      print "invalid field count" > "/dev/stderr"
      exit 2
    }
    if (count) printf "retries=%d mean_ms=%.1f\n", count, total/count
    else print "retries=0 mean_ms=unavailable"
  }
' events.tsv
```

Expected output is `retries=2 mean_ms=160.0`. This is a teaching schema, not a general TSV validator. It checks field count but does not reject every malformed numeric value, unknown outcome, duplicate event, or unexpected identifier. Before using it for an operational decision, add validation appropriate to the actual schema or use a language with clearer error reporting. The distinction matters: awk will convert strings in numeric expressions, which can disguise bad input. Its field and pattern model is specified by the [POSIX awk manual](https://man7.org/linux/man-pages/man1/awk.1p.html).

Sorting followed by `uniq -c` is useful for frequencies because uniq groups adjacent repeated lines. It does not combine identical values separated by other values. Set the locale when bytewise reproducibility is appropriate:

```bash
awk -F '\t' '$1 == "notification" { print $2 }' events.tsv |
  LC_ALL=C sort |
  uniq -c
```

That report counts notification outcomes in this fixture; it does not measure unique orders or customer impact. Retries can generate several events for one order. Always name the unit counted. Numeric sorting also requires numeric options; ordinary lexical ordering places `100` before `20`. Locale affects comparison and other text behavior, so record it when reproducibility matters. [GNU sort manual](https://man7.org/linux/man-pages/man1/sort.1.html).

## Structured logs preserve meaning

DispatchDesk will eventually log JSON objects with fields rather than require everyone to parse human sentences. Use jq to parse those objects. The following fixture contains one complete JSON object per line, commonly called JSON Lines. Create it in the same disposable directory:

```bash
cat > events.jsonl <<'EOF'
{"event":"notification","outcome":"sent","order_id":"order-1","latency_ms":40}
{"event":"notification","outcome":"retry","order_id":"order-2","latency_ms":120}
{"event":"order","outcome":"accepted","order_id":"order-3","latency_ms":12}
{"event":"notification","outcome":"retry","order_id":"order-4","latency_ms":200}
EOF
jq -r 'select(.event == "notification" and .outcome == "retry") | .order_id' events.jsonl
jq -s '[.[] | select(.event == "notification" and .outcome == "retry")] | length' events.jsonl
```

The first command prints two identifiers; the second prints `2`. Single quotes keep jq's expression intact for the shell. `-r` emits selected strings without JSON quoting; `-s` collects all input values into an array before applying the filter. Slurping is convenient for a tiny fixture but uses memory proportional to the input. Stream records for large searches, or use a bounded query in a log system. Treat raw identifiers as restricted incident data. jq parses JSON; field presence, allowed types, and business invariants still require validation. [jq official manual](https://jqlang.org/manual/).

Do not parse JSON with a grep expression that assumes field order or whitespace. Valid JSON can encode the same object differently. Nor should an extracted string be passed through `eval`: data must remain data. Chapter 11's quoting rules and Chapter 18's script validation are the boundary between a report and accidental command execution.

## Investigate a suspiciously clean report

Suppose Harbor's report shows zero retries while customers report delayed notifications. Start by preserving the report command, its status, the input path, collection time, and file metadata. Confirm whether the file represents the current worker instance and the relevant time interval. A perfectly parsed stale file is still misleading.

Run collection separately and inspect its stderr. Then inspect a bounded raw sample locally, checking the record format before applying a filter. Compare selected records with their original lines. If the report depends on a pipe, capture all stage statuses. If records come from several instances, establish whether the collection includes all of them and whether duplicate forwarding is possible.

In this scenario the collector lacked permission to read the rotated log. Its error went to the terminal, while `wc -l` successfully counted an empty stream. Restoring the intended read permission and collecting the missing interval reveals repeated retry events. Do not respond with broad recursive permission changes: Chapter 14 explains how to grant only the required access. Preserve the original failed collection as evidence, regenerate the report, and identify affected orders from the durable store before considering replay. A count of retry events alone cannot prove that an order is still undelivered.

The prevention is a collection contract: fail visibly on an unreadable source, keep diagnostics separate, record the interval and instance set, validate records, and name the counting unit. For Summit and Atlas the collector may query a centralized service rather than a local file, but incomplete pagination, wrong environment, and failed credentials recreate the same problem. Streaming syntax cannot replace collection completeness.

## Practice and review

1. Run the pipeline-status examples. Explain how a zero output count accompanies a failed producer. Guidance: the counter's success establishes only that it processed its available input; pipefail or individual statuses expose the upstream failure.
2. Change one fixture record to contain a fifth tab-separated field. Explain why the awk aggregate must be rejected even if it also prints useful values. Guidance: its exit status rejects the report's input contract; do not publish a partial aggregate as complete evidence.
3. Change JSON field order and add harmless whitespace. Confirm the jq selection still works. Then remove an outcome field. Guidance: parsing remains valid, but the record is excluded by the selection; schema validation should distinguish missing data from an ordinary nonmatching event.
4. Design a retry report for a 15-minute incident. State collection boundaries, instance coverage, duplicate handling, counting unit, and failure behavior. Guidance: distinguish event count, unique affected orders, and outstanding work; these answer different operational questions.

Before trusting a pipeline, ask whether you can explain its input schema, each transformation, each failure status, and the population represented by its output. These questions are more valuable than memorizing a long chain of commands.

After completing the exercises, remove only the three known fixture files while still inside your reader-owned practice directory:

```bash
rm -- result.txt events.tsv events.jsonl
```

Retain any evidence you deliberately created separately. Leave the practice directory only after confirming it contains no material you want to keep; do not recursively remove an unknown directory.

## Verification and takeaways

The author inspected the upstream Bash manual, POSIX awk specification, GNU sort manual, and jq official manual. The examples are local fixtures and require no running DispatchDesk service or infrastructure. Execution results are recorded in the chapter continuation summary; distribution images and real incident collectors have not been exercised.

Streams separate results from diagnostics. Pipes couple concurrent processes and propagate backpressure, while their status handling can hide upstream failures. Choose a parser that understands the record format, validate the schema, and count the unit you intend to measure. A useful report states what was collected as clearly as it states what was found.

Continue to [Chapter 14](014-users-groups-and-permissions.md) to diagnose access failures without weakening the whole host. Revisit [Chapter 7](../01-engineering-mental-models/007-learning-to-investigate.md) for the evidence discipline behind the suspicious-report investigation.
