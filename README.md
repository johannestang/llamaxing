<div align="center">

<img src="docs/cool_llama.png" alt="llamaxing logo" width="80%">

<h1>Llamaxing</h1>

[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/format.json)](https://github.com/astral-sh/ruff)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)
[![build](https://github.com/johannestang/llamaxing/actions/workflows/publish-image.yml/badge.svg)](https://github.com/johannestang/llamaxing/actions/workflows/publish-image.yml)

Llamaxing (pronounced "llama crossing") is a FastAPI-based API gateway for OpenAI compatible APIs.

[Features](#features) |
[Configuration](#configuration) |
[Examples](#examples)

</div>

## Features
Llamaxing is a modular API gateway that allows you to control traffic between users/applications and the (Azure) OpenAI API.
It comes with a number of modules, but can easily be extended to suit your particular needs. The main features are:

- Custom authentication/authorization flows
    - Built-in support for API key and [JWT](https://en.wikipedia.org/wiki/JSON_Web_Token) authentication
    - [Sidecar mode](https://learn.microsoft.com/en-us/azure/architecture/patterns/sidecar) with built-in support for API key and [Microsoft Entra ID](https://learn.microsoft.com/en-us/entra/identity/) authentication
- Logging of all request/responses for auditing and analytics
    - Built-in support for [MongoDB](https://www.mongodb.com/)
- Integration with observability platforms
    - Built-in support for [Langfuse](https://langfuse.com/) with automatic creation
    of traces/generations for requests sent to Llamaxing
- Load balancing across multiple OpenAI API deployments

The documentation for this project is still quite limited. For an overview of Llamaxing's functionality, take a look
at the [examples](#examples) below.

## Configuration
### Models
Llamaxing needs a list of models provided as a JSON file (by default called `models.json`). Examples are given [here](./examples/).
The file should contain a list of JSON objects with the following schema:

| Parameter | Type | Description | Options |
| ------------- | ---- | ----------- | ---- |
| `id` | string | Model name used when calling the API endpoints | | 
| `aliases` | string | List of alternative names for the model | |
| `capabilities` | list of strings | Type of model. Used to match models with API endpoints | `chat_completions`, `completions`, `embeddings`, `images_generations` |
| `instances` | list of objects | List of API deployments for the model. If more than one deployment is provided, Llamaxing will load balance across all deployments for the model. | |

The instance object has the following schema:

| Parameter | Type | Description | Options |
| ------------- | ---- | ----------- | ---- |
| `id` | string | ID of model/deployment combination. Must be unique | | 
| `provider` | string | API provider | `azure`, `openai` | 
| `openai_organization` | string | Organization ID passed to OpenAI API | `null` or any string | 
| `openai_api_key` | string | OpenAI API key | Literal API key or environment variable (see notes) | 
| `azure_endpoint` | string | Azure OpenAI deployment endpoint | | 
| `azure_deployment` | string | Azure OpenAI deployment name | Literal name or environment variable (see notes) | 
| `azure_api_key` | string | Azure OpenAI API key | Literal API key or environment variable (see notes) | 
| `azure_api_version` | string | Azure OpenAI API version | | 

Notes: 
1. Parameters prepended with `openai_` should only be included if the provider is OpenAI, likewise for Azure.
2. For parameters where it is noted, you can reference an environment
variable rather than specifying the actual value, e.g. `"${OPENAI_API_KEY}"`.
3. It is possible to mix Azure and OpenAI when specifying model API deployments.

### Identities
If authentication is enabled, Llamaxing needs a list the identities that are authorized to access the API. These identities can represent both users and applications. The list is provided as a JSON file (by default called `identities.json`).
The file should contain a list of JSON objects with the following schema:

| Parameter | Type | Description | 
| ------------- | ---- | ----------- |
| `id` | string | ID of the identity. Typically this would be application name, username or email address |  
| `auth_key` | string | Key used to identify the identity. Depends on the chosen auth. method. See below | 
| `name` | strings | Name of the identity |  
| `info` | object | Any additional information about the identity to be included in logging. Not used in Llamaxing |  
| `observability` | object | Parameters passed to observability client |  

The only observability platform currently supported is [Langfuse](https://langfuse.com/). To enable it for an identity, add the following parameters to the observability object:

| Parameter | Type | Description | 
| ------------- | ---- | ----------- |
| `langfuse_public_key` | string | Langfuse public key |  
| `langfuse_secret_key` | string | Langfuse secret key | 

### Llamaxing settings
Settings for Llamaxing are defined [here](./llamaxing/settings.py) and
can be set using environment variables or a `.env` file. The main settings are:

| Parameter | Type | Description | Options | Default |
| ------------- | ---- | ----------- | ------- | ------- |
| `app_name` | string | Application name | | `llamaxing` |
| `app_mode` | string | Application mode | `gateway`, `sidecar` | `gateway` |
| `app_requests_timeout` | int | Timeout limit when sending requests upstream | | 300 |
| `debug_level` | int | Controls how much is logged to the console | 0: No debugging information. 1: Requests, responses, and auth. details. 2: Raw streaming responses. 3: Sensitive information such as access tokens, use with caution! | 0 |
| `auth_method`| string | Authentication method | `none`, `apikey`, `jwt` | `none` |
| `identity_store`| string | Identity store | `none`, `json` | `none` |
| `logging_client`| string | Logging client | `none`, `mongodb` | `none` |
| `observability_client`| string | Observability client | `none`, `langfuse` | `none` |

For each parameter that defaults to `none`, there are additional parameters that should be set, if you change it to a different value.
For example, if you set `auth_method` to `jwt`, then there are a number of parameters (all starting with `auth_method_jwt_`) that you need to consider. See [settings.py](./llamaxing/settings.py) for a full list.


## Examples
### 1. No authentication
A good place to start is the simplest example: [01-simple-noauth](/examples/01-simple-noauth/). Here all modules (including authentication) are disabled.
To run it, you need to create a `.env` file in the folder with your API key based on either of the samples (depending on whether you use OpenAI or Azure) and bring up the container using docker compose:

```bash
docker compose up
```
You can now navigate to [http://localhost:8000/](http://localhost:8000/) to access the API docs, or try out one of the [demos](/examples/demos/).

### 2. API key authentication
In this example, [02-simple-apikey](/examples/02-simple-apikey/), we add API key authentication. In this scenario you have a number of users/applications that need access to OpenAI, but you
do not want to simply share your API key with all of them. Instead you assign each of them a unique API key and have them access OpenAI through
Llamaxing. 

Compared to the previous example we now set `AUTH_METHOD=apikey` and `IDENTITY_STORE=json` and create an [identities.json](./examples/02-simple-apikey/identities.json) file with a single identity. Note that the identity is identified by the API key it has been provided (`1234` in this example)
which is set using the `auth_key` parameter in `identities.json`. If you bring up the container with docker compose and access the documentation, you will see
that you now need to provide the API key, and you will see in the output from Llamaxing that the identity of the caller is logged when requests are made.

### 3. Azure and JWT
In the third example, [03-azure-jwt-oauth2-proxy](./examples/03-azure-jwt-oauth2-proxy/), authentication is now done using JSON Web Tokens (JWT).
Llamaxing can be configured to verify the signature of the JWTs (it isn't be default, but should be in a production environment), and it will
reject requests from unknown identities. However, typically you would deploy an authenticating proxy in front of Llamaxing that would
have already verified the JWT before passing it on to Llamaxing. In this example we use [OAuth2 Proxy](https://github.com/oauth2-proxy/oauth2-proxy), but 
often this would be handled by the ingress controller on your Kubernetes cluster.

The example uses Microsoft Entra ID as identity provider and assumes that you already have an Azure subscription. 
In order to run it, you will need to [create an app registration](https://learn.microsoft.com/en-us/entra/identity-platform/quickstart-register-app), 
and fill in all the relevant values in the `.env` file based on one of the sample files. All values that
need to be filled in are written in brackets, e.g. `<tenant id>`.

You can follow these steps to set up the app registration:
1. Note down your Tenant ID and the Client ID of your app registration.
2. Go to Certificates & secrets, create a client secret and note it down.
3. Go to Authentication -> Add platform -> Web and set the Redirect URI to `http://localhost:4180/oauth2/callback`.
4. Go to API permissions -> Add a permission -> Microsoft Graph -> Delegated permissions and select `email`, `offline_access`, `openid`, `profile` and click Add permissions.
5. Go to API permissions -> Grant admin consent for Default Directory.
6. Go to Manifest -> Edit the manifest to have `"accessTokenAcceptedVersion": 2` and save.

Based on this you now have most of the values needed to populate the `.env` file.
However, you also need to generate a cookie secret for OAuth2 Proxy. This can be done using the following:
```bash
python -c 'import os,base64; print(base64.urlsafe_b64encode(os.urandom(32)).decode())'
```

Since we now use Microsoft Entra ID, we will use the Object ID of users/applications to define
our identities. In the [Azure portal](https://portal.azure.com/) go to Microsoft Entra ID -> Users, 
find your user and note down the Object ID and fill it in as the value for `auth_key` in `identities.json` (using
`sample-identities.json` as a template).

Note, that while Llamaxing uses Object ID by default, this can be changed using the `auth_method_jwt_id_key` parameter.

You should now be able to bring up Llamaxing using `docker compose up` and access it through OAuth2 Proxy by navigating to
[http://localhost:4180/](http://localhost:4180/).

### 4. The full stack

This example, [04-azure-jwt-full-stack](./examples/04-azure-jwt-full-stack/), builds on the one above. We now add 
logging to [MongoDB](https://www.mongodb.com/) and observability using [Langfuse](https://langfuse.com/).
Furthermore, we include an instance of Llamaxing running in sidecar mode to show how authentication can be
off-loaded if your application doesn't support your authentication scheme.

In order to support these additions, we need to modify the app registration created above. On top of being used for 
single sign-on (SSO) in OAuth2 Proxy, as above, we will also use it for SSO in Langfuse, and it will provide
the identity needed to authenticate from the sidecar. Note, that it is purely for simplicity that we are using the same
app registration for all these purposes.

Go to the [Azure portal](https://portal.azure.com/), navigate to your app registration and do the following: 
1. Go to Expose an API -> Application ID URI / Add -> Save. Note down the Application ID URI which should be of the form: `api://<client id>`.
2. Go to Authentication -> Web / Add URI, add `http://localhost:3000/api/auth/callback/azure-ad` and save.
3. Go to Overview -> Managed application in local directory -> click on the name of the app registration. Note down the Object ID, this is the Enterprise Application Object ID.

Together with the values from the previous example you can now create a `.env` file based on one of the samples.
Langfuse needs two generated secrets, these can be created as in the previous example.

You also need to create an `identities.json` file based on the sample file, but before doing this you will need
to generate API keys for Langfuse:
1. Bring up the stack with `docker compose up`.
2. Navigate to [http://localhost:3000/](http://localhost:3000/) and log in to Langfuse.
3. Create a new project, go to Settings -> API keys -> Create new API keys. Note down the keys.

You now have all the details needed to populate `identities.json`. Once this is done, restart Llamaxing
to reload the configuration.

You now have a number of services running:
1. As in the previous example you can access Llamaxing through OAuth2 Proxy at [http://localhost:4180/](http://localhost:4180/), and
if you make a request you will see in the console output that you are identified by your Microsoft Entra ID user.
2. Llamaxing is also running in sidecar mode at [http://localhost:8000/](http://localhost:8000/). If you try to access it
you will see that you do not need to authenticate, but if you make a request you'll see in the console output that the
request is authenticated using the identity of the app registration. This mode is useful if you have an application that
needs access to OpenAI but isn't compatible with your authentication scheme. See [here](https://learn.microsoft.com/en-us/azure/architecture/patterns/sidecar) for more on this architectural pattern.
3. An instance of MongoDB is running and all requests will be logged to it.
4. As already mentioned, Langfuse is running at [http://localhost:3000/](http://localhost:3000/). Since the API keys
for Langfuse have been added to both identities in `identities.json` all request will also be visible in Langfuse. 
By default a request will be added to Langfuse as a trace with a single generation. The ID of the identity
that made the request will be added (as User ID) and model details will be filled in. If you want to add more
details and group multiple requests then you need to send the appropriate information in a custom field called `observation_metadata`.
See [demo-langfuse.py](./examples/demos/demo-langfuse.py) for an example.
