# Model Address Standard (MAS) v1.0

* Version: 1.0
* Status: Draft
* Last Updated: February 14, 2026

## 1. Abstract

The Model Address Standard (MAS) defines a minimal, client-side convention for identifying an AI model using a URI fragment parameter.

MAS enables portable, shareable references to specific models without modifying HTTP semantics or requiring server-side support.

MAS does not define transport behavior, authentication, message formats, or inference parameters.

## 2. Scope

MAS:

* Defines a single required fragment parameter: m
* Is processed entirely by clients
* Does not alter HTTP resource identity
* Requires no server, proxy, or infrastructure changes

If a client does not implement MAS, the URI behaves as a normal HTTP or HTTPS URL.

## 3. Syntax

A MAS address is any valid HTTP or HTTPS URI containing a fragment parameter m.

### 3.1 General Form

```
https://authority[:port][/path]#m=<model-identifier>
```

MAS is layered on top of RFC 3986.
This specification defines only fragment semantics and does not redefine URI grammar.

## 4. Required Parameter

### 4.1 Model Parameter (m)

The m parameter identifies the model to be used by the client.

Syntax

```
m = model-identifier
model-identifier = 1*( ALPHA / DIGIT / "-" / "_" / "." / "/" / ":" )
```

Requirements

* m MUST be present.
* m MUST NOT be empty.
* m is case-sensitive.
* Clients MUST percent-decode the value before use.
* Clients MUST treat m as opaque and provider-defined.

MAS does not define model naming conventions.

## 5. Processing Rules

When processing a MAS address:

1. Parse the URI according to RFC 3986.
2. Extract the fragment component.
3. Split the fragment on & into parameters.
4. Split each parameter on the first =.
5. Percent-decode parameter values.
6. Verify that m is present and non-empty.
7. Ignore all other parameters.
8. Apply the model identifier according to client implementation.

Fragment parsing MUST occur before percent-decoding to avoid ambiguity.


## 6. Unknown Parameters

Clients:

* MUST ignore unknown parameters.
* MUST preserve unknown parameters if reserializing the URI.

Future revisions of MAS may define additional standard parameters.

## 7. Canonical Form (Optional)

For consistent client-side comparison and deduplication:

* The scheme and authority SHOULD be lowercase.
* Fragment parameters SHOULD be sorted alphabetically.
* Default or empty parameters SHOULD be omitted.
* Percent-encoding SHOULD be minimal.

Note: Because the fragment is never sent to the server, canonicalization is purely a client concern and does not affect resource identity.

Example:

Canonical:

```
https://api.example.com#m=model-a
```

Non-canonical:

```
https://API.EXAMPLE.COM#x=1&m=model-a
```

## 8. Security Considerations

* MAS parameters are visible in browser history, logs, and referrer headers.
* MAS parameters are client-side metadata and MUST NOT be trusted without validation.
* Clients SHOULD restrict acceptable model identifiers according to local policy.
* MAS does not provide authentication, authorization, or integrity guarantees.

## 9. Examples

```
https://localhost:11434#m=mistral
```

```
https://api.anthropic.com#m=claude-sonnet-4-5
```

```
https://bedrock.us-east-1.amazonaws.com#m=anthropic.claude-v2
```

```
https://inference.company.io:8080#m=meta-llama/Llama-2-70b
```

```
https://models.example.com#m=huggingface.co:meta-llama/Llama-2-70b
```

## 10. Non-Goals

MAS does not define:

* Sampling parameters (e.g., temperature)
* Token limits
* System prompts
* API protocols
* Streaming formats
* Provider registries

Such concerns are intentionally out of scope.

## 11. References

RFC 3986 — Uniform Resource Identifier (URI): Generic Syntax


